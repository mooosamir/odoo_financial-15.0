from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    to_force_exchange_rate = fields.Float(
        string='Forzar T.C.',
        digits=(12, 12),
        help='This labels is used for force exchange rate.'
    )

    @api.onchange('currency_id', 'to_force_exchange_rate')
    def _onchange_to_force_exchange_rate(self):
        to_force_exchange_rate = self.to_force_exchange_rate
        company_id = self.company_id
        force_flag = to_force_exchange_rate != 0.0 and company_id.currency_id != self.currency_id
        for line in self.line_ids if self.move_type == 'entry' else self.invoice_line_ids:
            if force_flag:
                balance = line.currency_id._force_convert(line.amount_currency, company_id.currency_id, company_id, to_force_exchange_rate)
            else:
                balance = line.currency_id._convert(line.amount_currency, company_id.currency_id, company_id,
                                                    line.move_id.date or fields.Date.context_today(line))
            line.with_context(check_move_validity=False).debit = balance if balance > 0.0 else 0.0
            line.with_context(check_move_validity=False).credit = -balance if balance < 0.0 else 0.0
        self._recompute_dynamic_lines(recompute_all_taxes=True)

    def _get_actual_currency_rate(self):
        if self.to_force_exchange_rate != 0.0 and self.company_id.currency_id != self.currency_id:
            rate = 1 / self.to_force_exchange_rate
        else:
            rate = super(AccountMove, self)._get_actual_currency_rate()
        return rate

    @api.depends('currency_id', 'to_force_exchange_rate')
    def _compute_currency_rate(self):
        super(AccountMove, self)._compute_currency_rate()

    def get_tax_base_amount(self, tax_base_amount, currency_id):
        if self.to_force_exchange_rate:
            tax_base_amount = currency_id._force_convert(tax_base_amount, self.company_id.currency_id, self.company_id, self.to_force_exchange_rate)
        else:
            tax_base_amount = super(AccountMove, self).get_tax_balance(tax_base_amount, currency_id)
        return tax_base_amount

    def get_tax_balance(self, amount, currency_id):
        if self.to_force_exchange_rate:
            balance = currency_id._force_convert(amount, self.company_currency_id, self.company_id, self.to_force_exchange_rate)
        else:
            balance = super(AccountMove, self).get_tax_balance(amount, currency_id)
        return balance

    def action_register_payment(self):
        action = super().action_register_payment()
        for rec in self:
            to_force_exchange_rate = rec.to_force_exchange_rate
        action['context']['to_force_exchange_rate'] = to_force_exchange_rate
        return action


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _force_convert(self, from_amount, to_currency, company, force_rate, round=True):
        """Returns the converted amount of ``from_amount``` from the currency
           ``self`` to the currency ``to_currency`` for the given ``date`` and
           company.

           :param company: The company from which we retrieve the convertion rate
           :param round: Round the result or not
        """
        self, to_currency = self or to_currency, to_currency or self
        assert self, "convert amount from unknown currency"
        assert to_currency, "convert amount to unknown currency"
        assert company, "convert amount from unknown company"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            to_amount = from_amount * (1 / force_rate)
        # apply rounding
        return to_currency.round(to_amount) if round else to_amount
