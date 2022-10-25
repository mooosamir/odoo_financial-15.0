from odoo.tests.common import TransactionCase
from datetime import date


class TestAccountDiscountGlobal(TransactionCase):
    def setUp(self):
        super(TestAccountDiscountGlobal, self).setUp()
        self.model_move = self.env['account.move']
        self.model_line = self.env['account.move.line']
        self.model_account = self.env['account.account']
        self.currency_id_pen = self.env['res.currency'].search(
            [('name', '=', 'PEN')]
            )
        self.currency_id_usd = self.env['res.currency'].search(
            [('name', '=', 'USD')]
            )
        self.account_tax_group_id = self.env['account.tax.group'].create({
            'name': 'Grupo Impuesto - Test',
            'sequence': 2
        })

        self.account_type = self.env['account.account.type'].create({
            'name': 'account_type_1',
            'type': 'other',
            'internal_group': 'equity',
        })

        self.account_01 = self.model_account.create({
            'name': 'account 1',
            'code': '043',
            'user_type_id': self.account_type.id,
            'company_id': self.env.ref("base.main_company").id,
        })

        self.account_tax_id = self.env['account.tax'].create({
            'name': 'Impuesto - Test',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'company_id': self.env.ref("base.main_company").id,
            'sequence': 1,
            'amount': 20.0000,
            'tax_group_id': self.account_tax_group_id.id
        })

        self.product_tem = self.env['product.template'].create({
            'name': 'prod_1',
            'global_discount': True,
        })

        self.obj_product = self.env['product.product'].create({
            'name': 'product1',
            'lst_price': 100,
            'product_tmpl_id': self.product_tem.id,
        })

        self.journal_id_usd = self.env['account.journal'].create({
            'name': 'Diario Venta',
            'type': 'sale',
            'code': 'TestD',
            'currency_id': self.currency_id_usd.id
        })

        self.model_01 = self.model_move.create({
            'date': date.today(),
            'move_type': 'out_invoice',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.obj_product.id,
                'price_unit': 50.0,
                'debit': 50.50,
                'credit': 0.50,
                'amount_currency': 50.00,
                'currency_id': self.currency_id_pen.id,
            })],
        })

        self.model_02 = self.model_move.create({
            'date': date.today(),
            'move_type': 'out_invoice',
            'company_id': self.env.ref("base.main_company").id,
            'journal_id': self.journal_id_usd.id,
            'currency_id': self.currency_id_usd.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.obj_product.id,
                'price_unit': 30.0,
                'debit': 20.50,
                'credit': 1.50,
                'amount_currency': 8.00,
                'currency_id': self.currency_id_pen.id,
            })],
        })

    def test_01_global(self):
        self.assertEqual(self.model_01.discount_percent_global,
                         self.model_02.discount_percent_global)
        self.assertTrue(self.model_01.discount_percent_global)
        print('--------TEST -Descuento Global- OK-------')
