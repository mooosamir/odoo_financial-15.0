from odoo import api, fields, models


def get_narration_data(partner_id, partner2_id, note):
    departure_address = "Dirección de Partida: {}, {}, {}, {}, {}".format(
        partner_id.street or '', partner_id.l10n_pe_district.name or '', partner_id.city_id.name or '', partner_id.state_id.name or '',
        partner_id.country_id.name or '')
    arrival_address = "Dirección de Llegada: {}, {}, {}, {}, {}".format(
        partner2_id.street or '', partner2_id.l10n_pe_district.name or '', partner2_id.city_id.name or '', partner2_id.state_id.name or '',
        partner2_id.country_id.name or '')
    narration = note + '\n' if note else ''
    narration = '{}{}\n{}'.format(narration, departure_address, arrival_address)
    return narration


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['narration'] = get_narration_data(self.warehouse_id.partner_id, self.partner_shipping_id, self.note)
        return invoice_vals


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        invoice_vals['narration'] = get_narration_data(order.warehouse_id.partner_id, order.partner_shipping_id, order.note)
        return invoice_vals
