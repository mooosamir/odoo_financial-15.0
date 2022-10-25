{
    'name': 'Use classic format to print stock picking',
    'version': '15.0.0.1.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Add an additional, classic-style stock picking peruvian format.',
    'Description': """
    Add a peruvian classic format for stock picking, which is requested by many users
    """,
    'category': 'Warehouse',
    'depends': [
        'account',
        'stock',
        'qr_code_stock_picking',
        'l10n_latam_invoice_document',
        'l10n_pe_delivery_note',
        'qr_code_on_sale_invoice',
        'ple_permanent_inventory_in_physical_units',
        'merchandise_carrier',
        'contact_driver_license_number',
        'stock_picking_print_note'
    ],
    'assets': {'web.report_assets_common':
                   ['l10n_pe_classic_format_picking/static/src/css/main.css']},
    'data': [
        "reports/ticket_report.xml",
        "reports/ticket_template.xml",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 45.00
}
