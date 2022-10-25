from odoo.tests import common
from odoo.tests.common import Form


class TestDocumentType(common.TransactionCase):

    def setUp(self):
        super(TestDocumentType, self).setUp()

    def test_account_analytic(self):
        partner_view = Form(self.env['account.analytic.default'],
                            view='account.view_account_analytic_default_form'
                            )
        self.stock_id = self.env['stock.warehouse'].create({
            'code': 'cliente',
            'company_id': self.env.ref("base.main_company").id,
            'active': True,
            'sequence': 3,
        })

        partner_view.origin_warehouse_id = self.stock_id
        self.assertTrue(partner_view.origin_warehouse_id)

        print('--TEST OK - ACCOUNT ANALYTIC DEFAULT LOCATION--')
