from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products add weight (key = id+name+description+uom+weight) and corresponding values of interest."""
        res = super(StockMoveLine, self)._get_aggregated_product_quantities()

        for move_line in res.values():
            move_line["weight"] = move_line["product"].weight

        return res
