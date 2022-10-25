{
    'name': 'Cashier only uses his diaries',
    'version': '15.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': "In the dashboard view and when using the payment buttons, users will only see those journals to which they have been assigned.",
    'description': """
    In each Journal you assign one or more assigned users and when a user uses a Payment button, he will only see his assigned Cash and Bank journals.
     In the dashboard view, only those journals in which it has been assigned will appear to the user.
    """,
    'category': 'Accounting',
    'depends': ['account','base_setup'],
    'data': [
        'views/journal_views.xml',
        'security/groups.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 25.00,
    'uninstall_hook': '_uninstall_module_complete',
}
