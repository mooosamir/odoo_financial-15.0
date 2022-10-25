from odoo import models, fields, api


class AccountAnalyticDefault(models.Model):
    _inherit = 'account.analytic.default'

    origin_warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Almacén de Origen'
    )

    origin_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de Origen')

    dest_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de Destino')

    @api.model
    def account_get(self, product_id=None, partner_id=None, account_id=None, user_id=None, date=None, company_id=None, warehouse_id=None, location_id_01=None,
                    location_id_02=None):
        domain = []
        if product_id:
            domain += ['|', ('product_id', '=', product_id)]
        domain += [('product_id', '=', False)]
        if partner_id:
            domain += ['|', ('partner_id', '=', partner_id)]
        domain += [('partner_id', '=', False)]
        if account_id:
            domain += ['|', ('account_id', '=', account_id)]
        domain += [('account_id', '=', False)]
        if company_id:
            domain += ['|', ('company_id', '=', company_id)]
        domain += [('company_id', '=', False)]
        if user_id:
            domain += ['|', ('user_id', '=', user_id)]
        domain += [('user_id', '=', False)]
        if warehouse_id:
            domain += ['|', ('origin_warehouse_id', '=', warehouse_id)]
        domain += [('origin_warehouse_id', '=', False)]
        if location_id_01:
            domain += ['|', ('origin_location_id', '=', location_id_01)]
        domain += [('origin_location_id', '=', False)]
        if location_id_02:
            domain += ['|', ('dest_location_id', '=', location_id_02)]
        domain += [('dest_location_id', '=', False)]
        if date:
            domain += ['|', ('date_start', '<=', date), ('date_start', '=', False)]
            domain += ['|', ('date_stop', '>=', date), ('date_stop', '=', False)]
        best_index = -1
        res = self.env['account.analytic.default']
        for rec in self.search(domain):
            index = 0
            if rec.product_id:
                index += 1
            if rec.partner_id:
                index += 1
            if rec.account_id:
                index += 1
            if rec.company_id:
                index += 1
            if rec.user_id:
                index += 1
            if rec.date_start:
                index += 1
            if rec.date_stop:
                index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('product_id', 'account_id', 'partner_id', 'date', 'move_id.stock_move_id')
    def _compute_analytic_account_id(self):
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date_maturity,
                    company_id=record.move_id.company_id.id,
                    warehouse_id=record.move_id.stock_move_id.picking_type_id.warehouse_id.id,
                    location_id_01=record.move_id.stock_move_id.location_id.id,
                    location_id_02=record.move_id.stock_move_id.location_dest_id.id
                )
                record.analytic_account_id = (record._origin or record).analytic_account_id or rec.analytic_id
                record.analytic_tag_ids = (record._origin or record).analytic_tag_ids or rec.analytic_tag_ids
