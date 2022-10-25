from lxml import etree
from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res_view = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)

        if view_type == 'form':
            user = self.env.user
            doc = etree.XML(res_view['arch'])
            value = "//field[@name='journal_id']"
            for node in doc.xpath(value):
                node.attrib['domain'] = f"['&', '&', ('id', 'in', suitable_journal_ids),('assign_to', 'in', {user.id}) , ('type', 'in', ('purchase','general','situation','sale','bank','cash'))]"
            res_view['arch'] = etree.tostring(doc, encoding='unicode')

        return res_view