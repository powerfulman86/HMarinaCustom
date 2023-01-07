# -*- coding: utf-8 -*-
{
    'name': "Property Management",

    'summary': """
        custom module for property management for hurghada marina harbor""",

    'author': "I-Consultant",
    'website': "https://www.iconsultant-eg.com/",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Real Estate',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'sale_management', 'web_cohort', ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/sequence.xml',
        'views/menu_property_management.xml',
        'views/property_contract.xml',
        'views/property_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'images': ['static/description/banner.png'],
    'demo': ['demo/account_asset_demo.xml'],
    'auto_install': False,
    'installable': True,
    'application': True,
}
