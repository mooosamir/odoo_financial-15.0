from odoo import models


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def open_wizard_financial(self, options, params=None):
        my_date_from = False
        my_date_to = False
        if options.get('date'):
            if options['date'].get('date'):
                my_date_from = my_date_to = options['date']['date']
            else:
                my_date_from = options['date'].get('date_from')
                my_date_to = options['date'].get('date_to')
        wizard_form_id = self.env.ref('financial_statement_annexes.wizard_report_financial_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.report.financial',
            'views': [(wizard_form_id, 'form')],
            'view_id': wizard_form_id,
            'context': {
                'default_account_ids': [params.get('id')],
                'default_date_start': my_date_from,
                'default_date_end': my_date_to
            },
            'target': 'new'
        }


class AccountFinancialReport(models.Model):
    _inherit = 'account.financial.html.report'

    def _build_lines_hierarchy(self, options_list, financial_lines, solver, groupby_keys):
        lines = super(AccountFinancialReport, self)._build_lines_hierarchy(options_list, financial_lines, solver, groupby_keys)
        for line in lines:
            if line.get('caret_options') == 'account.account':
                if 'financial_report_group_' in line['id'] and line.get('parent_id', False):
                    str_format = 'financial_report_group_{}_'.format(line['parent_id'])
                    account_id = int(line['id'].replace(str_format, ''))
                elif '-account.financial.html.report.line-' in line['id'] and line.get('parent_id', False):
                    str_format = '{}|-account.account-'.format(line['parent_id'])
                    account_id = int(line['id'].replace(str_format, ''))
                else:
                    account_id = line['id']
                obj_account = self.env['account.account'].browse(account_id)
                line.update({
                    'account_id': obj_account.id,
                    'reconcile': obj_account.reconcile
                })
        return lines
