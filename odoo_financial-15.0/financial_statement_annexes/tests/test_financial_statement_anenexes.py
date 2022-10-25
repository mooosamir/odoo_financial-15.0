from odoo.tests.common import TransactionCase
from datetime import date

dat = date.today()


class TestSaleDocumentType(TransactionCase):

    def setUp(self):
        super(TestSaleDocumentType, self).setUp()
        self.wizard_report_model = self.env['wizard.report.financial']
        self.account_type_1 = self.env["account.account.type"].create(
            {
                'name': 'type_1',
                'type': 'other',
                'internal_group': 'equity',
            }
        )
        self.account_1 = self.env["account.account"].create(
            {
                'name': 'Cuenta',
                'code': 'cod_1',
                'user_type_id': self.account_type_1.id,
                'company_id': self.env.ref("base.main_company").id,
            }
        )

        self.data_report = {
            'date_start': dat,
            'date_end': dat,
            'xls_filename': 'Archivo',
            'xls_binary': False,
            'account_ids': [self.account_1.id],
        }

    def create_wizard_report_model(self, report_data):
        model_wizard = self.wizard_report_model.create(report_data)
        return model_wizard

    def test_wizard_report_model(self):
        in_data = self.create_wizard_report_model(self.data_report)
        self.assertTrue(in_data)
        print('------------TEST OK - CREATE------------')
