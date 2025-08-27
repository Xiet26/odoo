{
    'name': 'Sale Order Cost Management',
    'version': '1.0.4',
    'category': 'Sales/Sales',
    'summary': 'Manage additional costs for each sales order.',
    'description': """
        This module allows users to add and track various costs associated with a sales order directly on the order form.
    """,
    'author': 'Cascade (AI Assistant)',
    'website': '',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/sale_order_cost_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
