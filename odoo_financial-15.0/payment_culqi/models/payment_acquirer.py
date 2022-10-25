import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)



class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('culqi', 'Culqi')], ondelete={'culqi': 'set default'})
    culqi_public_key = fields.Char(string='Llave pública', required_if_provider='culqi', groups='base.group_system')
    culqi_private_key = fields.Char(string='Llave privada', required_if_provider='culqi', groups='base.group_system')

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist Culqi acquirers when the currency is not supported. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)
        currency = self.env['res.currency'].browse(currency_id).exists()
        # Currency codes in ISO 4217 format supported by Culqi.
        if currency and currency.name not in ('PEN', 'USD'):
            acquirers = acquirers.filtered(lambda a: a.provider != 'culqi')
        return acquirers
    
    def _culqi_get_api_url(self):
        """ Return the API URL according to the state.

        Note: self.ensure_one()

        :return: The API URL
        :rtype: str
        """
        self.ensure_one()
        if self.state == 'enabled':
            return '/payment/culqi/poll/'
        elif self.state == 'test':
            return '/payment/culqi/poll/'

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'culqi':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_culqi.payment_method_culqi').id