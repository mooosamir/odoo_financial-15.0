from odoo import api, fields, models
import re


class Partner(models.Model):
    _inherit = 'res.partner'

    l10n_pe_district = fields.Many2one(
        'l10n_pe.res.city.district', string='District',
        help='Districts are part of a province or city.')

    def _inverse_street_data(self):
        return self._compute_street_data()

    @api.depends('street')
    def _compute_street_data(self):
        street_fields = self._get_street_fields()
        for partner in self:
            if not partner.street:
                for field in street_fields:
                    partner[field] = None
                continue

            street_raw = partner.street
            vals = self._split_street_with_params(street_raw)
            if not vals:
                vals = ''
            else:
                vals = vals
            partner['street_number'] = ''.join(vals)
            partner['street_number2'] = ''
            partner['street_name'] = street_raw

    def _split_street_with_params(self, street_raw):
        vals = {}
        numbers_p = {}
        previous_pos = 0
        field_name = None
        data_address = ['nro', 'n°', 'numero', 'número']
        for list_data in data_address:
            if list_data in street_raw.lower():
                pos = street_raw.lower().rfind(list_data)
                vals = re.findall('[0-9]+', street_raw)
                for p in vals:
                    pnum = street_raw.rfind(p)
                    if pnum > pos:
                        numbers_p = p
                        break
                break
            else:
                vals = None
        return numbers_p
