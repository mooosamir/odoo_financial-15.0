from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    discount_percent_global = fields.Float(
        string='Descuento Global %',
        compute='_compute_amount',
        store=True
    )

    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        self._compute_discount_percent_global()

    def _compute_discount_percent_global(self):
        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===
                    if not line.exclude_from_invoice_tab and line.product_id.global_discount:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
            discount_percent_global = abs(total_untaxed_currency if len(currencies) == 1 else abs(total_untaxed))
            value = move.amount_untaxed + discount_percent_global
            move.discount_percent_global = (discount_percent_global / value) * 100 if value != 0 else 0

            # if subtotal advance != 0
            number_invoice_lines = 0
            for line in move.invoice_line_ids:
                number_invoice_lines += 1
                if number_invoice_lines == 1 and line.product_id.global_discount:
                    move.discount_percent_global = 0.00


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    global_discount = fields.Boolean(string='Descuento Global')
