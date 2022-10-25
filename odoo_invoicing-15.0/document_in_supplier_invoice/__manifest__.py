{
    'name': 'Use document type in supplier invoices',
    'version': '15.0.2.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': "For each type of document, you can decide whether it will be used for the supplier voucher record...",
    'description': """
    Configure in each type of document, the purchase journal with which this type of document can be used. It is very 
    useful for countries where different types of tax documents are distinguished, as is the case in many Latin American countries.
    """,
    'category': 'Accounting',
    'depends': ['account','l10n_latam_invoice_document'],
    'data': [
        'views/latam.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 35.00,
}
