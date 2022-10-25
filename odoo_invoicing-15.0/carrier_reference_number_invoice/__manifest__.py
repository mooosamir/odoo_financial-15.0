{
    'name': 'Field for carrier reference number on the invoice',
    'version': '15.0.1.1.4',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': '''
    Add a Field in the invoice to place the reference number related to the invoice.
    ''',
    'Description': '''
    Add a Field in the invoice to place the reference number related to the invoice.
    ''',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'data/invoice_template.xml',
        'views/account_move.xml',
        'data/functions_data.xml',
    ],
    'uninstall_hook': '_refactor_xml',
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
