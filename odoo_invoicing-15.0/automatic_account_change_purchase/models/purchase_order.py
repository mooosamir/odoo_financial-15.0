from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'purchase.order'

    def action_view_invoice(self, invoices=False):
        if not invoices:
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids
        for invoice in invoices:
            invoice._get_change_account()
        res = super(SaleOrder, self).action_view_invoice(invoices)
        return res
