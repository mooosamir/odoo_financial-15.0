from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoice(self, order, so_line, amount):
        move = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        move._get_change_account()
        return move
