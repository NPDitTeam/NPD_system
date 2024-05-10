{
    'name': 'NPD Standard : Asset Repairs',
    'version': '14.0.3',
    'sequence': 230,
    'summary': 'Repair damaged products',
    'description': """""",
    'depends': ["mail", "stock", "repair","account", "account_asset_management", "npd_std_asset_menu"],
    "author": "npd",
    "website": "https://npd9.com/",
    'category': 'Accounting & Finance',
    'data': [
        'security/ir.model.access.csv',
        'security/repair_security.xml',
        'views/repair_views.xml',
        'data/ir_sequence_data.xml',
    ],
    'demo': ['data/repair_demo.xml'],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}