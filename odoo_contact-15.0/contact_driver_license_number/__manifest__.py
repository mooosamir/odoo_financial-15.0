{
    'name': 'Contact driver license number',
    'version': '15.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co',
    'summary': 'Add the driver\'s license number field in the employee form.',
    'category': 'Contact',
    'depends': [
        'l10n_latam_base',
        'stock'
    ],
    'data': [
        'views/base_views.xml',
        'static/src/xml/contact_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
