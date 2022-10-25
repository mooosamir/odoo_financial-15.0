from odoo import api, models

class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    @api.constrains('name', 'currency_id', 'company_id')
    def _constraint_currency_rate_unique_name_per_day(self):
        return