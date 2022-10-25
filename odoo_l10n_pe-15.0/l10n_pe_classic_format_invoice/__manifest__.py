{
    'name': 'l10n pe fields for classic format invoice',
    'version': '15.0.1.2.7',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module will be used to make the classic invoice compatible for the Peruvian localization.',
    'category': 'All',
    "depends": ['account',
                'l10n_pe',
                'l10n_pe_edi',
                'classic_format_invoice',
                'qr_code_on_sale_invoice',
    ],
    'data': ['views/classic_format_template.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
