from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_is_zero, float_round


class AccountAccountType(models.Model):
    _inherit = "account.account"

    related_user_account_name = fields.Char(related='user_type_id.name')


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    factor_round = fields.Float(
        string="Factor de Redondeo",
        digits="Account",
        help="En este campo se colocará el factor por el cual quiere que se redondee la línea del término de plazo, si quiere que salga sin decimales, colocar 1.00.",
    )

    term_extension = fields.One2many('account.payment.term.line.extension',
                                     string='Cuenta contables',
                                     inverse_name='payment_term_line_id',
                                     default=False,
                                     )

    def compute_line_amount(self, total_amount, remaining_amount, precision_digits):
        """Compute the amount for a payment term line.
        In case of procent computation, use the payment
        term line rounding if defined

            :param total_amount: total balance to pay
            :param remaining_amount: total amount minus sum of previous lines
                computed amount
            :returns: computed amount for this line
        """
        self.ensure_one()
        if self.value == "fixed":
            return float_round(self.value_amount, precision_digits=precision_digits)
        elif self.value in ("percent", "percent_amount_untaxed"):
            amt = total_amount * self.value_amount / 100.0
            if self.factor_round:
                amt = float_round(amt, precision_rounding=self.factor_round)
            return float_round(amt, precision_digits=precision_digits)
        elif self.value == "balance":
            return float_round(remaining_amount, precision_digits=precision_digits)
        return None


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def compute(self, value, date_ref=False, currency=None):
        self.ensure_one()
        date_ref = date_ref or fields.Date.context_today(self)
        amount = value
        sign = value < 0 and -1 or 1
        result = []
        precision_digits = currency.decimal_places
        if not currency and self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(self.env.context['currency_id'])
        elif not currency:
            currency = self.env.company.currency_id
        for line in self.line_ids:
            if line.value == 'fixed':
                amt = sign * currency.round(line.value_amount)
            elif line.value == 'percent':
                amt = line.compute_line_amount(value, amount, precision_digits)
            elif line.value == 'balance':
                amt = currency.round(amount)
            next_date = fields.Date.from_string(date_ref)
            if line.option == 'day_after_invoice_date':
                next_date += relativedelta(days=line.days)
                if line.day_of_the_month > 0:
                    months_delta = (line.day_of_the_month < next_date.day) and 1 or 0
                    next_date += relativedelta(day=line.day_of_the_month, months=months_delta)
            elif line.option == 'after_invoice_month':
                next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                next_date = next_first_date + relativedelta(days=line.days - 1)
            elif line.option == 'day_following_month':
                next_date += relativedelta(day=line.days, months=1)
            elif line.option == 'day_current_month':
                next_date += relativedelta(day=line.days, months=0)

            term_value = self.get_payment_term_line_values(next_date, amt, line)
            term_value += (line,)
            result.append(term_value)
            amount -= amt
        amount = sum(line[1] for line in result)
        dist = currency.round(value - amount)
        if dist:
            last_date = result and result[-1][0] or fields.Date.context_today(self)
            term_value = self.get_payment_term_line_values(last_date, dist)
            term_value += (False,)
            result.append(term_value)

        return result
