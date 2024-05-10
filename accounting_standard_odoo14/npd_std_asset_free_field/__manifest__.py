{
    "name": "NPD Standard : Asset Free Field And Sequences",
    "summary": """Asset Sequences""",
    "version": "14.0.3",
    "license": "AGPL-3",
    "development_status": "Beta",
    "author": "npd",
    'website': 'https://npd9.com/',
    "depends": ["account_asset_management", "npd_asset_qrcode"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_asset_free_field_view.xml",
        "views/account_condition_type.xml",
    ],
    "installable": True,
}
