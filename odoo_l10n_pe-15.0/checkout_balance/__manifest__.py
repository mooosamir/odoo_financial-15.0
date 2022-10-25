{
    'name': 'Checkout balance',
    'version': '15.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Creates the trial balance report that includes the income statement by nature and by function.',
    'category': 'Accounting',
    'depends': ['account_reports'],
    'data': [
        'views/account_views.xml',
        'views/report_financial.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 30.00
}
