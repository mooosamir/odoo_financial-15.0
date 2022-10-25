from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ubigeo = fields.Char(
        string='Ubigeo',
        size=6,
        default='150101',
        help='Aquí se consigna el código de ubicación geográfica (Ubigeo) de 6 dígitos, de acuerdo Catálogo N° 13 de SUNAT.'
    )
    annexed_establishment = fields.Char(
        string='Establecimientos Anexos',
        default='0000',
        help='Código asignado por SUNAT para el establecimiento anexo declarado en el RUC.'
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            tags = ['ubigeo', 'annexed_establishment']
            res = self.tags_invisible_per_country(tags, res, [self.env.ref('base.pe')])
        return res
