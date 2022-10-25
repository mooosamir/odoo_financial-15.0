from odoo import models


class WizardReportFinancial(models.TransientModel):
    _inherit = 'wizard.report.financial'

    def _set_values(self, obj_move_line):
        values = super(WizardReportFinancial, self)._set_values(obj_move_line)
        values.update({
            'expected_pay_date': obj_move_line.expected_pay_date or '',
            'next_action_date': obj_move_line.next_action_date or '',
            'internal_note': obj_move_line.internal_note or '',
        })
        return values
