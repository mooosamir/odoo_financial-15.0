from odoo import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_number = fields.Char(
        string='N° Guía',
        copy=False
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            tags = ['picking_number']
            res = self.env['res.partner'].tags_invisible_per_country(tags, res, [self.env.ref('base.pe')])
        return res
