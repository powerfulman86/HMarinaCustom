# -*- coding: utf-8 -*-
{
    'name': "Hurghada Marina",
    'summary': """
        This module adds all Hurghada Marina customization""",

    'description': """
        This module adds all Hurghada Marina customization
    """,
    'author': "Instant Solutions 4 You",
    'website': "https://inst-sol4u.com",
    'category': 'Customizations',
    'version': '0.1',
    'depends': [
        'account',
        'base',
        'hr',
        'product',
        'purchase',
        'sale',
        'stock',
        'uom',
    ],
    'data': [
        'data/uom_data.xml',
        'data/product_data.xml',
        'security/ir.model.access.csv',
        'views/account_account_views.xml',
        'views/hm_boat_pricing_views.xml',
        'views/hr_employee_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/stock_quant_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
