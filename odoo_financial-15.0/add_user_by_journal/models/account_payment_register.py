from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountPaymentRegister, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            user = self.env.user
            domain = res['fields']['journal_id']['domain']
            domain_trans = domain[0]
            add_domain_field = f" '&', ('assign_to', 'in', {user.id}) , ('type', 'in', ('purchase','general','situation','sale','bank','cash'))]"
            res['fields']['journal_id']['domain'] = domain_trans + add_domain_field

        return res
