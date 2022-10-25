from odoo import api, fields, models


class PaymentTermLineExt(models.Model):
    _name = "account.payment.term.line.extension"

    payment_term_line_id = fields.Many2one('account.payment.term.line')

    currency = fields.Many2one('res.currency',
                               string='Moneda',
                               required=False)

    ledger_account = fields.Many2one('account.account',
                                     string='Cuenta contable por cobrar',
                                     default=False,
                                     help="Al colocar una cuenta contable, el plazo de pago se generará en esa cuenta contable.",
                                     required=False,
                                     )

    ledger_account_payable = fields.Many2one('account.account',
                                             string='Cuenta contable por pagar',
                                             default=False,
                                             required=False,
                                             )
