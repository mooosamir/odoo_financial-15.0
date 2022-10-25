from odoo.tests.common import TransactionCase
from odoo.tests.common import Form
from datetime import datetime

dat = datetime.now()


class TestAccountDiscountGlobal(TransactionCase):
    def setUp(self):
        super(TestAccountDiscountGlobal, self).setUp()
        self.model_sale_order = self.env["sale.order"]
        self.model_partner = self.env["res.partner"]

    def create_sale_order(self, partner):
        sale_01 = {
            "name": "sale_1",
            "date_order": dat,
            "state": "draft",
            "partner_id": partner.id,
            "partner_invoice_id": partner.id,
            "partner_shipping_id": partner.id,
            "company_id": self.env.ref("base.main_company").id,
        }
        return self.model_sale_order.create(sale_01)

    def create_res_partner(self):
        data_res_partner = {"name": "Cliente - Prueba", "company_type": "person"}
        return self.model_partner.create(data_res_partner)

    def test_prepare_invoice_values(self):
        res_01 = self.create_res_partner()
        sale_1 = self.create_sale_order(res_01)
        advance_payment = Form(
            self.env["sale.advance.payment.inv"].with_context(
                {"active_ids": [sale_1.id], "open_invoices": True}
            ),
            view="sale.view_sale_advance_payment_inv",
        )
        advance_payment.advance_payment_method = "percentage"
        advance_payment.amount = 5
        action_01 = advance_payment.save().create_invoices()
        x = action_01["res_id"]
        y = self.env["account.move"].browse(x)
        self.assertTrue(y.narration)
        print("--------TEST -Sale Advance Payment inv- OK-------")
