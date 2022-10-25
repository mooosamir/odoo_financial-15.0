from odoo import api, fields, models

from dateutil.relativedelta import relativedelta


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def get_payment_term_line_values(self, payment_date, payment_value, payment_line=False):
        result = (fields.Date.to_string(payment_date), payment_value)
        return result

    def compute(self, value, date_ref=False, currency=None):
        self.ensure_one()
        date_ref = date_ref or fields.Date.context_today(self)
        amount = value
        sign = value < 0 and -1 or 1
        result = []
        if not currency and self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(self.env.context['currency_id'])
        elif not currency:
            currency = self.env.company.currency_id
        for line in self.line_ids:
            if line.value == 'fixed':
                amt = sign * currency.round(line.value_amount)
            elif line.value == 'percent':
                amt = currency.round(value * (line.value_amount / 100.0))
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
            result.append(self.get_payment_term_line_values(next_date, amt, line))
            amount -= amt
        amount = sum(line[1] for line in result)
        dist = currency.round(value - amount)
        if dist:
            last_date = result and result[-1][0] or fields.Date.context_today(self)
            result.append(self.get_payment_term_line_values(last_date, dist))
        return result


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Payment term lines calc
    def _get_payment_terms_computation_date(self, today):
        """ Get the date from invoice that will be used to compute the payment terms.
        :param self:    The current account.move record.
        :return:        A datetime.date object.
        """
        if self.invoice_payment_term_id:
            return self.invoice_date or today
        else:
            return self.invoice_date_due or self.invoice_date or today

    def _tax_tags_need_inversion(self, move, is_refund, tax_type):
        """ Tells whether the tax tags need to be inverted for a given move.

        :param move: the move for which we want to check inversion
        :param is_refund: whether or not the operation we want the inversion value for is a refund
        :param tax_type: the tax type of the operation we want the inversion value for

        :return: True if the tags need to be inverted
        """
        if move.move_type == 'entry':
            return (tax_type == 'sale' and not is_refund) or (tax_type == 'purchase' and is_refund)
        return False

    def _get_payment_terms_account(self, payment_terms_lines):
        """ Get the account from invoice that will be set as receivable / payable account.
        :param self:                    The current account.move record.
        :param payment_terms_lines:     The current payment terms lines.
        :return:                        An account.account record.
        """
        if payment_terms_lines:
            # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
            return payment_terms_lines[0].account_id
        elif self.partner_id:
            # Retrieve account from partner.
            if self.is_sale_document(include_receipts=True):
                return self.partner_id.property_account_receivable_id
            else:
                return self.partner_id.property_account_payable_id
        else:
            # Search new account.
            domain = [
                ('company_id', '=', self.company_id.id),
                ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
            ]
            return self.env['account.account'].search(domain, limit=1)

    def _compute_payment_terms(self, date, total_balance, total_amount_currency):
        """ Compute the payment terms.
        :param self:                    The current account.move record.
        :param date:                    The date computed by '_get_payment_terms_computation_date'.
        :param total_balance:           The invoice's total in company's currency.
        :param total_amount_currency:   The invoice's total in invoice's currency.
        :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
        """
        if self.invoice_payment_term_id:
            to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.company_id.currency_id)
            if self.currency_id == self.company_id.currency_id:
                # Single-currency.
                return [(b[0], b[1], b[1]) for b in to_compute]
            else:
                # Multi-currencies.
                to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date, currency=self.currency_id)
                return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
        else:
            return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

    def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute, in_draft_mode, today):
        """
        Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
        :param self:                    The current account.move record.
        :param existing_terms_lines:    The current payment terms lines.
        :param account:                 The account.account record returned by '_get_payment_terms_account'.
        :param to_compute:              The list returned by '_compute_payment_terms'.
        """
        # As we try to update existing lines, sort them by due date.
        existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
        existing_terms_lines_index = 0

        # Recompute amls: update existing line or create new one for each payment term.
        new_terms_lines = self.env['account.move.line']
        for comp_tuple in to_compute:
            balance = comp_tuple[1]
            currency = self.journal_id.company_id.currency_id
            if currency and currency.is_zero(balance) and len(to_compute) > 1:
                continue

            if existing_terms_lines_index < len(existing_terms_lines):
                # Update existing line.
                candidate = existing_terms_lines[existing_terms_lines_index]
                existing_terms_lines_index += 1
            else:
                # Create new line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                candidate = create_method({
                    'name': self.payment_reference or '',
                    'quantity': 1.0,
                    'move_id': self.id,
                    'currency_id': self.currency_id.id,
                    'account_id': account.id,
                    'partner_id': self.commercial_partner_id.id,
                    'exclude_from_invoice_tab': True,
                })
            candidate.update(self.get_compute_candidate_values(comp_tuple, balance))
            new_terms_lines += candidate
            if in_draft_mode:
                candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
        return new_terms_lines

    # New method from _compute_diff_payment_terms_lines
    def get_compute_candidate_values(self, data_tuple, balance):
        candidate_values = {
            'date_maturity': data_tuple[0],
            'amount_currency': -data_tuple[2],
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0
        }
        return candidate_values

    # Central method to calculate payment terms
    def _recompute_payment_terms_lines(self):
        """
            Compute the dynamic payment term lines of the journal entry.
        """
        self.ensure_one()
        self = self.with_company(self.company_id)
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_company(self.journal_id.company_id)

        existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = self._get_payment_terms_computation_date(today)
        account = self._get_payment_terms_account(existing_terms_lines)
        to_compute = self._compute_payment_terms(computation_date, total_balance, total_amount_currency)
        new_terms_lines = self._compute_diff_payment_terms_lines(existing_terms_lines, account, to_compute, in_draft_mode, today)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity

    # Dynamic move lines calc
    def _recompute_tax_lines(self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None):
        """ Compute the dynamic tax lines of the journal entry.

        :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                is_refund = move.move_type in ('out_refund', 'in_refund')
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
                price_unit_wo_discount = base_line.amount_currency

            balance_taxes_res = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
            )

            if move.move_type == 'entry':
                repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
                repartition_tags = base_line.tax_ids.flatten_taxes_hierarchy().mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
                tags_need_inversion = self._tax_tags_need_inversion(move, is_refund, tax_type)
                if tags_need_inversion:
                    balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
                    for tax_res in balance_taxes_res['taxes']:
                        tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids

            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # The tax line is no longer used in any base lines, drop it.
            if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

            # Don't create tax lines with zero balance.
            if currency.is_zero(taxes_map_entry['amount']):
                if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            # tax_base_amount field is expressed using the company currency.
            tax_base_amount = self.get_tax_base_amount(taxes_map_entry['tax_base_amount'], currency)

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
                continue

            balance = self.get_tax_balance(taxes_map_entry['amount'], currency)

            to_write_on_line = {
                'amount_currency': taxes_map_entry['amount'],
                'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }

            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                if tax_rep_lines_to_recompute and taxes_map_entry['tax_line'].tax_repartition_line_id not in tax_rep_lines_to_recompute:
                    continue

                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)

                if tax_rep_lines_to_recompute and tax_repartition_line not in tax_rep_lines_to_recompute:
                    continue

                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    #'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))

    def get_tax_base_amount(self, tax_base_amount, currency_id):
        tax_base_amount = currency_id._convert(tax_base_amount, self.company_id.currency_id, self.company_id, self.date or fields.Date.context_today(self))
        return tax_base_amount

    def get_tax_balance(self, amount, currency_id):
        balance = currency_id._convert(amount, self.company_currency_id, self.company_id, self.date or fields.Date.context_today(self))
        return balance
