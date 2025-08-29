{
    'name': 'Sale Order Cost Management',
    'version': '1.2.0',
    'category': 'Sales/Sales',
    'summary': 'Manage additional costs for each sales order with Excel export.',
    'description': """
        This module allows users to:
        - Add and track various costs associated with a sales order
        - Calculate cost price and margins for order lines
        - Export detailed sale order data to Excel format
        - Export warranty documents to Word format
        - Track profitability of sales with comprehensive reporting
        - Manage commercial terms for each order
    """,
    'author': 'Cascade (AI Assistant)',
    'website': '',
    'depends': ['sale_management', 'custom_product_info'],
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
