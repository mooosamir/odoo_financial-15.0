from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    number_license = fields.Char(string='Numero de Licencia')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one(
        string='Conductor',
        comodel_name='res.partner'
    )
