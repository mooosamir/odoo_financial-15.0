from odoo import models, fields, api


class AccountFullReconcile(models.Model):
    _inherit = 'account.full.reconcile'

    reconcile_date = fields.Date(
        string='Fecha de Reconciliación',
        compute='_compute_reconcile_date',
        store=True
    )

    @api.depends('reconciled_line_ids', 'reconciled_line_ids.date')
    def _compute_reconcile_date(self):
        for rec in self:
            if rec.reconciled_line_ids:
                rec.reconcile_date = max(rec.reconciled_line_ids.mapped(lambda x: x.date))
            else:
                rec.reconcile_date = False
