from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def unlink(self):
        if self.user_has_groups('delete_posted_journal_entries.group_account_delete'):
            self.superunlink()
        res = super(AccountMove, self).unlink()
        return res

    def superunlink(self):
        for move in self:
            move.posted_before = False
            move.write({
                'state': 'draft',
            })
            aml_reconcile_ids = [aml for aml in move.line_ids if aml.full_reconcile_id]
            if not len(aml_reconcile_ids):
                pass
            else:
                for aml_reconcile in aml_reconcile_ids:
                    aml_reconcile.remove_move_reconcile()
