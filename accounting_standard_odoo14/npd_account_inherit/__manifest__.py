# -*- coding: utf-8 -*-
{
    'name': "NPD Standard : Account Inherit",
    'summary': "npd_account_inherit",
    'description': "npd_account_inherit",
    "author": "Perfect Blending",
    "website": "https://npd9.com/",
    'category': 'Uncategorized',
    'version': '14.0.1',
    'depends': ['base',
                'account',
                'account_cheque',
                'account_billing',
                'account_voucher'
                ],
    'data': [
        'views/view_inherit_customer.xml',
        'views/view_inherit_vendor.xml',
    ],

}
