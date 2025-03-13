{
    'name': 'Custom Product Information',
    'version': '1.0',
    'category': 'Sales/Sales',
    'summary': 'Add custom fields to product for detailed information',
    'description': """
        This module adds additional fields to products including:
        - Manufacturer
        - Model
        - Part Number
        - Warranty
        - Origin
        - Technical Specifications (VI/EN)
        - Package Includes (VI/EN)
        - Documents
        - HS Code
        - Customs Description
        - Estimated Import Tax
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
} 