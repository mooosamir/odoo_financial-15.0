{
    'name': 'Unrealized gains and losses for foreign currency',
    'version': '15.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': "Adjusts the gain and loss for unrealized exchange rate difference.",
    'description': """
    Calculates the exchange rate difference of the accounting accounts in foreign currency and records the accounting 
    entry for the difference automatically. Allows you to set different exchange rates for the same currency, for different 
    accounts. Which is very useful if the exchange rate for accounting Assets and Liabilities differs in your country.
    """,
    'category': 'Accounting',
    'depends': ['financial_statement_annexes'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_financial_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 229.00
}
