from lxml import etree
from odoo import api, models, fields
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def tags_invisible_per_country(self, tags, res_view, countries):
        """
        This method should be called in fields_view_get.
        Example:
            tags = [('span', 'dispatch_advice_state_div'), ('button', 'action_send_data_sunat'), ('page', 'peruvian_efact'), 'dispatch_sequence_id']
            res = self.env['res.partner'].tags_invisible_per_country(self, tags, res)

        :param tags: list of tags to hide in views (It could a name of specific field or tuple to hide specific tag by name)
        :param res_view: response of fields_view_get method
        :param countries: list of contries to apply restrictions
        :return: Overwritten response of fields_view_get method
        """
        peruvian_company = self.env.company.country_id in countries
        if peruvian_company:
            return res_view
        doc = etree.XML(res_view['arch'])
        for tag in tags:
            if isinstance(tag, tuple):
                value = "//{}[@name='{}']".format(tag[0], tag[1])
            else:
                value = "//field[@name='{}']".format(tag)
            for node in doc.xpath(value):
                modifiers = {'invisible': 1}
                node.set("modifiers", json.dumps(modifiers))
        res_view['arch'] = etree.tostring(doc, encoding='unicode')
        return res_view
