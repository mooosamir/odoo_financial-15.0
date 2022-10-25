{
    'name': 'Field for aditional document reference on the invoice',
    'version': '15.0.0.1.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'We are going to add some new fields in the invoice (account.move) so that it is later sent in XML tags.',
    'description': "We are going to add some new fields in the invoice (account.move) so that it is later sent in XML tags.",
    'category': 'Accounting',
    'depends': ['account_discount_global'],
    'data': [
        'data/2.1/edi_templates.xml',
        'views/move_views.xml',
        'data/2.1/functions_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'uninstall_hook': '_refactor_xml',
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
