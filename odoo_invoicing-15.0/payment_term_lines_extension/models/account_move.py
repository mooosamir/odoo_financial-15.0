from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def _recompute_payment_terms_lines(self):
        """
            Compute the dynamic payment term lines of the journal entry.
        """
        self.ensure_one()
        self = self.with_company(self.company_id)
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_company(self.journal_id.company_id)

        # Change to solve a bug with lines
        existing_terms_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable') or line.date_maturity)
        others_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable') and not line.date_maturity)

        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = self._get_payment_terms_computation_date(today)
        account = self._get_payment_terms_account(existing_terms_lines)
        to_compute = self._compute_payment_terms(computation_date, total_balance, total_amount_currency)
        new_terms_lines = self._compute_diff_payment_terms_lines(existing_terms_lines, account, to_compute,
                                                                 in_draft_mode, today)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity

        # Ejecuta funcionalidad del módulo automatic_account_change, para que pueda funcionar junto a este
        self._get_change_account()

    def _get_payment_terms_account(self, payment_terms_lines):
        """ Get the account from invoice that will be set as receivable / payable account.
        :param self:                    The current account.move record.
        :param payment_terms_lines:     The current payment terms lines.
        :return:                        An account.account record.
        """

        if self.partner_id:
            # Retrieve account from partner.
            if self.is_sale_document(include_receipts=True):
                return self.partner_id.property_account_receivable_id
            else:
                return self.partner_id.property_account_payable_id

        elif payment_terms_lines:
            # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
            return payment_terms_lines[0].account_id
        else:
            # Search new account.
            domain = [
                ('company_id', '=', self.company_id.id),
                ('internal_type', '=',
                 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
            ]
            return self.env['account.account'].search(domain, limit=1)

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
        line_index = 0

        invoice_payment_term_lines = self.invoice_payment_term_id.line_ids
        currency_id = self.currency_id.id
        for comp_tuple in to_compute:
            balance = comp_tuple[1]
            currency = self.journal_id.company_id.currency_id

            if currency and currency.is_zero(balance) and len(to_compute) > 1:
                line_index += 1
                continue

            new_account = account.id
            if line_index < len(invoice_payment_term_lines):
                account_line_ids = invoice_payment_term_lines[line_index].term_extension

                account_line = account_line_ids.search(
                    [('currency.id', '=', currency_id), ('id', 'in', account_line_ids.ids)])
                ledger_account_related = account_line.ledger_account
                ledger_account_payable_related = account_line.ledger_account_payable

                if ledger_account_related and self.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                    new_account = ledger_account_related
                elif ledger_account_payable_related and self.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
                    new_account = ledger_account_payable_related

            if existing_terms_lines_index < len(existing_terms_lines):
                # Update existing line.
                candidate = existing_terms_lines[existing_terms_lines_index]
                existing_terms_lines_index += 1
            else:
                # Create new line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                    'account.move.line'].create
                candidate = create_method({
                    'name': self.payment_reference or '',
                    'quantity': 1.0,
                    'move_id': self.id,
                    'currency_id': self.currency_id.id,
                    'account_id': new_account,
                    'partner_id': self.commercial_partner_id.id,
                    'exclude_from_invoice_tab': True,
                })

            change = self.get_compute_candidate_values(comp_tuple, balance)
            change['account_id'] = new_account
            candidate.update(change)

            line_index += 1
            new_terms_lines += candidate

            if in_draft_mode:
                candidate.update(candidate._get_fields_onchange_balance(force_computation=True))

        return new_terms_lines
