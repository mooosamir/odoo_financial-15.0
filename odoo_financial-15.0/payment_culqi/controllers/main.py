from culqi.client import Culqi
from culqi.resources import Charge, Token
from odoo.http import request

from odoo import http
from odoo.exceptions import ValidationError

class CulqiController(http.Controller):

    
    @http.route('/payment/culqi/poll', type='http', auth="public", website=True, csrf=False)
    def culqi_form_feedback(self, **post):
        if '__website_sale_last_tx_id' not in request.session:
            raise ValidationError('¡ERROR!\n Intente de nuevo o avise a su administrador de sistemas.')
        transaction_id = request.session['__website_sale_last_tx_id']
        obj_transaction = request.env['payment.transaction'].sudo().browse(int(transaction_id))
        amount_value = 'Pagar {}{} {}'.format(
            obj_transaction.currency_id.symbol,
            obj_transaction.amount,
            obj_transaction.currency_id.name or post.get('currency')
        )
        if 'base_url' in request.session:
            base_url = request.session['base_url']
        else:
            base_url = '/shop/confirm_order'

        values = {
            'data_transaction': transaction_id,
            'amount_value': amount_value,
            'data_url': '/payment/culqi/return',
            'base_url': base_url,
            'default_partner_mail': obj_transaction.partner_id.email,
            'default_partner_name': obj_transaction.partner_id.name
        } 
        return request.render("payment_culqi.token_culqi_form", values)

    @http.route('/payment/culqi/return', type='http', auth="none", methods=['POST'], csrf=False, 
        save_session=False)
    def culqi_return_from_redirect(self, **post):
        """ Process the data returned by Culqi after redirection.

        The route is flagged with `save_session=False` to prevent Odoo from assigning a new session
        to the user if they are redirected to this route with a POST request. Indeed, as the session
        cookie is created without a `SameSite` attribute, some browsers that don't implement the
        recommended default `SameSite=Lax` behavior will not include the cookie in the redirection
        request from the payment provider to Odoo. As the redirection to the '/payment/status' page
        will satisfy any specification of the `SameSite` attribute, the session of the user will be
        retrieved and with it the transaction which will be immediately post-processed.

        :param dict data: The feedback data to process
        """
        
        post_data = self.culqi_verification_data(post)            
        transaction = post_data.get('transaction')
        card_number = post_data.get('card_number')
        cvv = post_data.get('cvv')
        email = post_data.get('email')
        expiration_month = post_data.get('expiration_month')
        expiration_year = post_data.get('expiration_year')

        try:
            obj_transaction = request.env['payment.transaction'].sudo().browse(transaction)
            amount = obj_transaction.amount
            values = {
                'amount': int(amount * 100),
                'currency_code': obj_transaction.currency_id.name,
                'description': obj_transaction.reference,
                'order': obj_transaction.reference,
                'email': email
            }            
            obj_acquirer = obj_transaction.acquirer_id
            culqi_obj = Culqi(public_key=obj_acquirer.culqi_public_key, private_key=obj_acquirer.culqi_private_key)

            # Token generation
            token_obj = Token(client=culqi_obj)
            token_data = {
                'card_number': card_number,
                'cvv': cvv,
                'email': email,
                'expiration_month': expiration_month,
                'expiration_year': expiration_year
            }
            token = token_obj.create(data=token_data)
            if token.get('object') == 'error':
                return {
                    'Error': token.get('merchant_message')
                }
            if token.get('error'):
                return {
                    'Error': token.get('error')
                }

            charge_res = self.culqi_charge(culqi_obj, token, values)            
            data = {
                'amount': amount,
                'currency': values['currency_code'],
                'reference': values['order'],
                'state': 'cancel' if not charge_res[0] else 'done'
            }
            
            request.env['payment.transaction'].sudo()._handle_feedback_data('culqi', data)            
            if charge_res[0]:
                return request.redirect('/payment/status')
            return {'Error': charge_res[1]}
        except ValidationError:
            return {
                'Error': 'No se pudo procesar la compra'
            }
        except Exception as excep_val:
            return {
                'Error': 'No se pudo procesar la compra: \n{}'.format(excep_val)
            }

    @staticmethod
    def culqi_verification_data(post):
        expiry_list = post['expiry'].replace(' ', '').split("/")
        card_number = post['number'].replace(' ', '')
        post_data = {
            'transaction': int(post['transaction']),
            'card_number': int(card_number),
            'cvv': int(post['cvc']),
            'email': post['email'],
            'expiration_month': int(expiry_list[0]),
            'expiration_year': int(expiry_list[1])
        }
        return post_data
    
    @staticmethod
    def culqi_charge(culqi_obj, token, values):
        charge_data = {
            'amount': values['amount'],
            'capture': True,
            'currency_code': values['currency_code'],
            'description': values['description'],
            'email': values['email'],
            'installments': 0,
            'metadata': {'order_id': values['order']},
            'source_id': token['data']['id']
        }
        charge_obj = Charge(client=culqi_obj)
        charge = charge_obj.create(data=charge_data)
        if charge['data'].get('object') != 'charge':
            return False, charge['data'].get('merchant_message')
        return True, 'Cargo exitoso'
