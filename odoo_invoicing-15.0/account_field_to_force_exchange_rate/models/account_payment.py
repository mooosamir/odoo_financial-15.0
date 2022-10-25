from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    to_force_exchange_rate = fields.Float(
        string='Forzar T.C.',
        digits=(12, 12),
        help='This labels is used for force exchange rate.'
    )

    def _synchronize_to_moves(self, changed_fields):
        super(AccountPayment, self)._synchronize_to_moves(changed_fields)
        for payment in self:
            payment.move_id._onchange_to_force_exchange_rate()
