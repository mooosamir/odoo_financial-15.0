{
    'name': 'Delete posted journal entries',
    'version': '15.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': "Add a special permission so that certain users can delete published accounting entries.",
    'description': """
    This module does not change the native operation of Odoo. The original control measures that Odoo incorporates 
    are maintained, it only creates an exception treatment, similar to the one we already have in bank statements, 
    where the reconciliation can be reversed and entries that have previously been Published can be eliminated.
    """,
    'category': 'Accounting',
    'data': [
        'security/account_move_security.xml',
    ],
    'depends': ['account'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 35.00
}
