from odoo import api, fields, models


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    def action_subscription_invoice(self):
        """update invoices with new current account"""
        invoices = self.env['account.move'].search([('invoice_line_ids.subscription_id', 'in', self.ids)])
        for invoice in invoices:
            invoice._get_change_account()
        res = super(SaleSubscription, self).action_subscription_invoice()
        return res
