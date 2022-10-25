from lxml import etree
from odoo import api, models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res_view = super(AccountPayment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            user = self.env.user
            doc = etree.XML(res_view['arch'])
            value = "//field[@name='journal_id']"
            for node in doc.xpath(value):
                domain = node.attrib['domain']
                domain_trans = domain[0]
                add_domain_field = f" '&', ('assign_to', 'in', {user.id}) , ('type', 'in', ('purchase','general','situation','sale','bank','cash'))]"
                node.attrib['domain'] = domain_trans + add_domain_field
            res_view['arch'] = etree.tostring(doc, encoding='unicode')

        return res_view
