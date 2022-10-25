from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float(
        string='Tipo de Cambio',
        digits=(12, 6),
        compute='_compute_currency_rate',
        store=True
    )

    @api.depends('currency_id')
    def _compute_currency_rate(self):
        for obj in self:
            obj.exchange_rate = obj._get_actual_currency_rate()

    def _get_actual_currency_rate(self):
        if self.currency_id:
            date = self.date or self.invoice_date or fields.Date.today()
            company = self.company_id
            currency_rates = self.currency_id._get_rates(company, date)
            exchange_rate = currency_rates.get(self.currency_id.id) or 1.0
            rate = 1 / (exchange_rate or 1)
        else:
            rate = 1
        return rate
