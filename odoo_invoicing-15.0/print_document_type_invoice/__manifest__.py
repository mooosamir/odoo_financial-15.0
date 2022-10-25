{
    'name': 'Print document type invoice',
    'version': '15.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': """
In Invoice printing formats, it replaces the name of the company and customer identification document. Instead of "NIF" and "Tax ID", 
enter the type of document set in the business partner. Add the name of the type of tax identification document on the invoice.
    """,
    'category': 'Accounting',
    'depends': [
        'account',
        'web',
        'document_type_validation',
        'report_vat_position'
    ],
    'data': ['static/src/xml/qweb_templates.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 4.00
}
