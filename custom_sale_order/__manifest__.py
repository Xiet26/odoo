{
    'name': 'Custom Sale Order',
    'version': '17.0.1.0.0',
    'summary': 'Quản lý chi phí gắn với đơn bán hàng',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_cost_line_views.xml',
    ],
    'installable': True,
    'application': False,
} 