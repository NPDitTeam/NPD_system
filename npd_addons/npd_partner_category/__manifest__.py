{
    "name": "NPD Partner Category",
    "summary": """Partner Category""",
    "version": "14.0.1",
    "license": "AGPL-3",
    "author": "npd",
    'website': 'https://npd9.com/',
    "depends": ["contacts","base","psn_is_customer_is_vendor"],
    "data": [
        "security/ir.model.access.csv",
        "views/partner_category_view.xml",

    ],
    "installable": True,
}
