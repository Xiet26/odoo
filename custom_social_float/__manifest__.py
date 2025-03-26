{
    'name': 'Social Float Buttons',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Floating social media buttons for website',
    'description': """
        This module adds floating social media buttons to your website.
        Features:
        - Floating buttons for Zalo, Facebook and Phone
        - Easy configuration through backend
        - Custom SVG icons support
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/social_float_views.xml',
        'views/social_float_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_social_float/static/src/css/social_float.css',
            'custom_social_float/static/src/js/social_float.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
} 