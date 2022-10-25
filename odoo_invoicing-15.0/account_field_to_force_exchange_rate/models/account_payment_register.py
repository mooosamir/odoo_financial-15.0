from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_batch(self, batch_result):
        values = super()._create_payment_vals_from_batch(batch_result)
        values = {'to_force_exchange_rate': self._context.get('to_force_exchange_rate'), **values}
        return values

    def _create_payment_vals_from_wizard(self):
        payment_vals = super()._create_payment_vals_from_wizard()
        payment_vals['to_force_exchange_rate'] = self._context.get('to_force_exchange_rate')
        return payment_vals

    def _init_payments(self, to_process, edit_mode=False):
        payments = super()._init_payments(to_process, edit_mode=edit_mode)
        for payment in payments:
            for move_id in payment.move_id:
                move_id._onchange_to_force_exchange_rate()
        return payments
