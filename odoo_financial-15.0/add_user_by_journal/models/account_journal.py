from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    assign_to = fields.Many2many('res.users', string='Asignado a', groups='add_user_by_journal.group_assign_to')
