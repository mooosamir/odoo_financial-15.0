from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    pay_sell_force_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Forzar cuenta por cobrar o pagar'
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(AccountMove, self)._onchange_partner_id()
        self._get_change_account()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        super(AccountMove, self)._onchange_invoice_line_ids()
        self._get_change_account()

    def _get_change_account(self):
        if self.journal_id and self.currency_id:
            account_input = False
            account_output = False
            if self.pay_sell_force_account_id:
                if self.move_type in ['out_invoice', 'out_refund']:
                    account_input = self.partner_id.property_account_receivable_id
                elif self.move_type in ['in_invoice', 'out_refund']:
                    account_input = self.partner_id.property_account_payable_id
                account_output = self.pay_sell_force_account_id
            else:
                account_change = self.env['account.change.by.type'].search([
                    ('journal_id', '=', self.journal_id.id),
                    ('currency_id', '=', self.currency_id.id)
                ], limit=1)
                if account_change:
                    if self.move_type in ['out_invoice', 'out_refund']:
                        account_input = self.partner_id.property_account_receivable_id
                        account_output = account_change.sale_account_id
                    elif self.move_type in ['in_invoice', 'in_refund']:
                        account_input = self.partner_id.property_account_payable_id
                        account_output = account_change.purchase_account_id

            if account_input and account_output:
                obj_line_filter = self.line_ids.filtered(lambda x: x.account_id.id == account_input.id)
                obj_line_filter.update({
                    'account_id': account_output.id
                })
