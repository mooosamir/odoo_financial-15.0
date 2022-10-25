{
    'name': 'Culqi Payment Acquirer',
    'version': '15.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Payment Acquirer: Culqi Implementation',
    'category': 'eCommerce',
    'depends': ['payment'],
    'data': [
        'views/acquirer_views.xml',
        'views/templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_culqi/static/src/js/card_lib.js',
            'payment_culqi/static/src/js/culqi_form.js',
            'payment_culqi/static/src/css/culqi.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'uninstall_hook': 'uninstall_hook',
    'currency': 'USD',
    'price': 99.99
}
