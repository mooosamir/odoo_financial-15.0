{
    'name': 'Financial Statement Annexes',
    'version': '15.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': "Accounts receivable and payable reports with cut-off date and aging reports.",
    'description': """
    Add the annexes menu in accounting reports, along with all the logic to allow accounts receivable and payable reports with cut-off date and aging reports
    """,
    'category': 'Accounting',
    'depends': ['add_reconcile_date'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_financial_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 120.00
}
