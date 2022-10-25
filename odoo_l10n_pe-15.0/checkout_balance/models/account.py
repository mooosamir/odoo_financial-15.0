from odoo import _, api, fields, models


class AccountGroup(models.Model):
    _inherit = 'account.group'

    type_group = fields.Selection(
        selection=[
            ('balance', 'Balance'),
            ('function', 'Resultado por función'),
            ('default', 'Resultado por Naturaleza'),
            ('both', 'Ambos Resultados')
        ],
        help='El atributo que complete en este campo, determina en qué columna del balance de comprobación aparecerá el saldo',
        string='Tipo de grupo'
    )


class AccountCheckoutBalanceAccountReport(models.AbstractModel):
    _name = "account.checkout.balance.report"
    _description = "Checkout Balance Report"
    _inherit = "account.report"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = True
    filter_analytic = True
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    MAX_LINES = None

    @api.model
    def _get_columns(self, options):
        header1 = [
                      {'name': '', 'style': 'width:40%'},
                      {'name': _('Initial Balance'), 'class': 'number', 'colspan': 2},
                  ] + [
                      {'name': period['string'], 'class': 'number', 'colspan': 2}
                      for period in reversed(options['comparison'].get('periods', []))
                  ] + [
                      {'name': options['date']['string'], 'class': 'number', 'colspan': 2},
                      {'name': 'Saldo Final', 'class': 'number', 'colspan': 2}
                  ] + [
                      # {'name': '', 'style': 'width:40%'},
                      {'name': 'Balance General', 'class': 'number', 'colspan': 2}
                  ] + [
                      # {'name': '', 'style': 'width:40%'},
                      {'name': 'EERR por Función', 'class': 'number', 'colspan': 2}
                  ] + [
                      # {'name': '', 'style': 'width:40%'},
                      {'name': 'EERR por Naturaleza', 'class': 'number', 'colspan': 2}
                  ]
        header2 = [
            {'name': '', 'style': 'width:40%'},
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
        ]
        if options.get('comparison') and options['comparison'].get('periods'):
            header2 += [
                           {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
                           {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
                       ] * len(options['comparison']['periods'])
        header2 += [
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},

            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast '},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast '},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
            {'name': _('Debit'), 'class': 'number o_account_coa_column_contrast '},
            {'name': _('Credit'), 'class': 'number o_account_coa_column_contrast'},
        ]
        return [header1, header2]

    @api.model
    def _get_lines(self, options, line_id=None):
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute all sums/unaffected earnings/initial balances for all comparisons.
        new_options = options.copy()
        new_options['unfold_all'] = True
        options_list = self._get_options_periods_list(new_options)
        accounts_results, taxes_results = self.env['account.general.ledger']._do_query(options_list, fetch_lines=False)

        lines = []
        grouped_by_account_group = []
        account_groups = {}
        extra_cols = 6
        normal_length = (2 * (len(options_list) + 2))
        length_col = normal_length + extra_cols

        # Add lines, one per account.account record.
        for account, periods_results in accounts_results:
            sums = []
            account_balance = 0.0
            for i, period_values in enumerate(reversed(periods_results)):
                account_sum = period_values.get('sum', {})
                account_un_earn = period_values.get('unaffected_earnings', {})
                account_init_bal = period_values.get('initial_balance', {})

                if i == 0:
                    # Append the initial balances.
                    initial_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
                    sums += [
                        initial_balance > 0 and initial_balance or 0.0,
                        initial_balance < 0 and initial_balance or 0.0,
                    ]
                    account_balance += initial_balance

                # Append the debit/credit columns.
                sums += [
                    account_sum.get('debit', 0.0) - account_init_bal.get('debit', 0.0),
                    account_sum.get('credit', 0.0) - account_init_bal.get('credit', 0.0),
                ]
                account_balance += sums[-2] - sums[-1]

            # account.account report line.
            columns = []
            for i, value in enumerate(sums):
                columns.append({'name': self.format_value(value, blank_if_zero=True), 'class': 'number', 'no_format_name': value})

            lines.append({
                'id': account.id,
                'columns': columns,
            })
            if account.group_id:
                if not account_groups.get(account.group_id.id, False):
                    name = account.group_id.name_get()[0][1]
                    if len(name) > 40 and not self._context.get('print_mode'):
                        name = name[:40] + '...'
                    account_groups.setdefault(account.group_id.id, {
                        'group_name': name,
                        'type_group': account.group_id and account.group_id.type_group or '',
                        'account_ids': [account.id],
                    })
                else:
                    account_groups[account.group_id.id]['account_ids'].append(account.id)

        totals = [0.0] * length_col
        for group_dict in account_groups:
            group_name = account_groups[group_dict]['group_name']
            account_ids = account_groups[group_dict]['account_ids']
            type_group = account_groups[group_dict]['type_group']

            filter_lines = list(filter(lambda z: z['id'] in account_ids, lines))
            if filter_lines:
                tmp_new_cols = [0.0] * (normal_length - 2)
                for line in filter_lines:
                    cols = line['columns']
                    for i in range(0, len(cols)):
                        tmp_new_cols[i] += cols[i]['no_format_name']

                new_cols = [0.0] * length_col
                final_total_debit, final_total_credit = normal_length - 2, normal_length - 1
                line_balance = 0.0
                flag = False
                for i in range(0, length_col):
                    if flag:
                        totals[i] += abs(new_cols[i])
                        continue
                    if i in [0, 1]:
                        if i == 0:
                            line_balance += abs(tmp_new_cols[i])
                        else:
                            line_balance -= abs(tmp_new_cols[i])
                        new_cols[i] += abs(tmp_new_cols[i])
                    elif i not in [final_total_debit, final_total_credit]:
                        if i % 2 == 0:
                            line_balance += tmp_new_cols[i] - tmp_new_cols[i + 1]
                        new_cols[i] += tmp_new_cols[i]
                    else:
                        if i == final_total_debit:
                            new_cols[i] += line_balance > 0 and line_balance or 0.0
                        elif i == final_total_credit:
                            new_cols[i] += line_balance < 0 and -line_balance or 0.0
                            if type_group == 'balance':
                                new_cols[i + 1] += new_cols[i - 1] if new_cols[i - 1] != 0 else 0.0
                                new_cols[i + 2] += new_cols[i] if new_cols[i] != 0 else 0.0
                            if type_group in ['function', 'both']:
                                new_cols[i + 3] += new_cols[i - 1] if new_cols[i - 1] != 0 else 0.0
                                new_cols[i + 4] += new_cols[i] if new_cols[i] != 0 else 0.0
                            if type_group in ['default', 'both']:
                                new_cols[i + 5] += new_cols[i - 1] if new_cols[i - 1] != 0 else 0.0
                                new_cols[i + 6] += new_cols[i] if new_cols[i] != 0 else 0.0
                            flag = True
                    totals[i] += abs(new_cols[i])

                grouped_by_account_group.append({
                    'id': group_dict,
                    'name': group_name,
                    'title_hover': group_name,
                    'columns': [{'name': self.format_value(col, blank_if_zero=True), 'class': 'number'} for col in new_cols],
                    'unfoldable': False,
                    'caret_options': 'account.group',
                    'account_ids': account_ids,
                    'class': 'o_account_searchable_line o_account_coa_column_contrast',
                })

        # Totals report lines.
        grouped_by_account_group.append({
            'id': 'grouped_accounts_total',
            'name': _('Total'),
            'class': 'total o_account_coa_column_contrast',
            'columns': [{'name': self.format_value(total), 'class': 'number'} for total in totals],
            'level': 1,
        })
        new_cols_positions = (list(range(length_col - extra_cols, length_col)))
        flag = False
        total_periods_cols = []
        for i, total in enumerate(totals):
            if i not in new_cols_positions:
                total_periods_cols.append({'name': ''})
                continue
            if not flag:
                x = total
                y = totals[i + 1]
                if y < x:
                    total_periods_cols.append({'name': '', 'value': 0.0})
                    total_periods_cols.append({'name': self.format_value(abs(x - y), blank_if_zero=True), 'class': 'number', 'value': abs(x - y)})
                else:
                    total_periods_cols.append({'name': self.format_value(abs(x - y), blank_if_zero=True), 'class': 'number', 'value': abs(x - y)})
                    total_periods_cols.append({'name': '', 'value': 0.0})
                flag = True
            else:
                flag = False
        grouped_by_account_group.append({
            'id': 'grouped_accounts_total',
            'name': 'Resultado del Ejercicio o periodo',
            'class': 'total o_account_coa_column_contrast',
            'columns': total_periods_cols,
            'level': 1,
        })
        totals_cols = []
        for i, total in enumerate(totals):
            if i not in new_cols_positions:
                totals_cols.append({'name': ''})
                continue
            totals_cols.append({'name': self.format_value(total + float(total_periods_cols[i]['value'])), 'class': 'number'})

        grouped_by_account_group.append({
            'id': 'grouped_accounts_total',
            'name': 'Totales',
            'class': 'total o_account_coa_column_contrast',
            'columns': totals_cols,
            'level': 1,
        })
        return grouped_by_account_group

    @api.model
    def _get_report_name(self):
        return "Comprobación x Cuenta"

    def open_account_group(self, options, params=None):
        active_id = int(params.get('id'))
        line = self.env['account.group'].browse(active_id)
        return {
            'name': line.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.group',
            'view_mode': 'form',
            'view_id': False,
            'views': [(False, 'form')],
            'res_id': line.id,
        }
