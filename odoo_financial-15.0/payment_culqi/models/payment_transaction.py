import logging

from odoo import api, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError

from odoo.addons.payment_transfer.controllers.main import TransferController

_logger = logging.getLogger(__name__)



class CulqiPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
        
    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Culqi-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'culqi':
            return res

        rendering_values = {
            'api_url': self.acquirer_id._culqi_get_api_url(),
            'item_name': '%s: %s' % (self.company_id.name, self.reference),
            'amount': self.amount,
            'reference': self.reference,
            'currency_code': self.currency_id.name,
        }
        return rendering_values
    
    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Culqi data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction"""
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'culqi':
            return tx
        reference, amount = data.get('reference'), data.get('amount')
        if not reference or not amount:
            raise ValidationError("Culqi: " + _("received data with missing reference (%s) or amount (%s)" % (reference, amount)))
        tx = self.search([('reference', '=', reference), ('provider', '=', 'culqi')])
        if not tx or len(tx) > 1:
            error_msg = _("Authorize: received data for reference %s' % reference")
            if not tx:
                error_msg += _("; no order found")
            else:
                error_msg += _("; multiple order found")
            raise ValidationError(error_msg)
        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Culqi data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_feedback_data(data)
        if self.provider != 'culqi':
            return

        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            logging_values = {
                'amount': data.get('amount', '0.0'),
                'total': self.amount,
                'fees': self.fees,
                'reference': self.reference,
            }
            _logger.error(
                "the paid amount (%(amount)s) does not match the total + fees (%(total)s + "
                "%(fees)s) for the transaction with reference %(reference)s", logging_values
            )
            raise ValidationError("Culqi: " + _("The amount does not match the total + fees."))
        if data.get('currency') != self.currency_id.name:
            raise ValidationError(
                "Culqi: " + _(
                    "The currency returned by Culqi %(rc)s does not match the transaction "
                    "currency %(tc)s.", rc=data.get('currency'), tc=self.currency_id.name
                )
            )
        
        status = data.get('status')
        if status == 'done':
            self._set_done()
