{
    'name': 'Tributary address extension',
    'version': '15.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """
This module will add the fields "Ubigeo" and "Establishment Annex" in the contact form. These fields are dependency for many modules of the Peruvian localization such as electronic invoicing.
    """,
    'depends': ['l10n_country_filter'],
    'data': ['views/partner_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
