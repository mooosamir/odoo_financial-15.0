import time
from odoo.addons.account.tests.common import TestAccountReconciliationCommon


class TestAddReconcileDate(TestAccountReconciliationCommon):

    def test_partial_reconcile_currencies_01(self):
        print("""
        
        
        --------------------------
        Funcionoooooooo
        -------------------------
        
        
        """)
        # Setting up rates for USD (main_company is in EUR)
        self.env['res.currency.rate'].create({'name': time.strftime('%Y') + '-' + '07' + '-01',
                                              'rate': 0.5,
                                              'currency_id': self.currency_usd_id,
                                              'company_id': self.company.id})

        self.env['res.currency.rate'].create({'name': time.strftime('%Y') + '-' + '08' + '-01',
                                              'rate': 0.75,
                                              'currency_id': self.currency_usd_id,
                                              'company_id': self.company.id})

        self.env['res.currency.rate'].create({'name': time.strftime('%Y') + '-' + '09' + '-01',
                                              'rate': 0.80,
                                              'currency_id': self.currency_usd_id,
                                              'company_id': self.company.id})

        # Preparing Invoices (from vendor)
        invoice_a = self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_agrolait_id,
            'currency_id': self.currency_usd_id,
            'invoice_date': '%s-07-01' % time.strftime('%Y'),
            'date': '%s-07-01' % time.strftime('%Y'),
            'invoice_line_ids': [
                (0, 0, {'product_id': self.product.id,
                        'quantity': 1, 'price_unit': 50.0})
            ],
        })
        invoice_b = self.env['account.move'].with_context(default_move_type='in_invoice').create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_agrolait_id,
            'currency_id': self.currency_usd_id,
            'invoice_date': '%s-08-01' % time.strftime('%Y'),
            'date': '%s-08-01' % time.strftime('%Y'),
            'invoice_line_ids': [
                (0, 0, {'product_id': self.product.id,
                        'quantity': 1, 'price_unit': 50.0})
            ],
        })
        (invoice_a + invoice_b).action_post()

        # Preparing Payments
        # One partial for invoice_a (fully assigned to it)
        payment_a = self.env['account.payment'].create({'payment_type': 'outbound',
                                                        'amount': 25,
                                                        'currency_id': self.currency_usd_id,
                                                        'journal_id': self.bank_journal_euro.id,
                                                        'company_id': self.company.id,
                                                        'date': time.strftime('%Y') + '-' + '07' + '-01',
                                                        'partner_id': self.partner_agrolait_id,
                                                        'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                                                        'partner_type': 'supplier'})

        # One that will complete the payment of a, the rest goes to b
        payment_b = self.env['account.payment'].create({'payment_type': 'outbound',
                                                        'amount': 50,
                                                        'currency_id': self.currency_usd_id,
                                                        'journal_id': self.bank_journal_euro.id,
                                                        'company_id': self.company.id,
                                                        'date': time.strftime('%Y') + '-' + '08' + '-01',
                                                        'partner_id': self.partner_agrolait_id,
                                                        'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                                                        'partner_type': 'supplier'})

        # The last one will complete the payment of b
        payment_c = self.env['account.payment'].create({'payment_type': 'outbound',
                                                        'amount': 25,
                                                        'currency_id': self.currency_usd_id,
                                                        'journal_id': self.bank_journal_euro.id,
                                                        'company_id': self.company.id,
                                                        'date': time.strftime('%Y') + '-' + '09' + '-01',
                                                        'partner_id': self.partner_agrolait_id,
                                                        'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                                                        'partner_type': 'supplier'})

        payment_a.action_post()
        payment_b.action_post()
        payment_c.action_post()

        # Assigning payments to invoices
        debit_line_a = payment_a.line_ids.filtered(
            lambda l: l.debit and l.account_id == self.account_rsa)
        debit_line_b = payment_b.line_ids.filtered(
            lambda l: l.debit and l.account_id == self.account_rsa)
        debit_line_c = payment_c.line_ids.filtered(
            lambda l: l.debit and l.account_id == self.account_rsa)

        invoice_a.js_assign_outstanding_line(debit_line_a.id)
        invoice_a.js_assign_outstanding_line(debit_line_b.id)
        invoice_b.js_assign_outstanding_line(debit_line_b.id)
        invoice_b.js_assign_outstanding_line(debit_line_c.id)

        # Asserting correctness (only in the payable account)
        full_reconcile = False
        reconciled_amls = (debit_line_a + debit_line_b + debit_line_c + (invoice_a + invoice_b).mapped('line_ids')) \
            .filtered(lambda l: l.account_id == self.account_rsa)

        # test
        dates = [payment_a.date, payment_b.date, payment_c.date]

        for aml in reconciled_amls:
            self.assertTrue(max(dates) == aml.full_reconcile_id.reconcile_date)
        print('------------TEST OK ------------')
