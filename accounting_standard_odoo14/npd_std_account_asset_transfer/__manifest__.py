{
    "name": "NPD Standard : Account Assets Transfer",
    "version": "14.0.2",
    "license": "AGPL-3",
    "depends": ["account","account_asset_management","npd_std_asset_menu"],
    "excludes": ["account_asset"],
     "author": "npd",
    "website": "https://npd9.com/",
    "category": "Accounting & Finance",
    "data": [
        # "security/account_asset_security.xml",
         "security/ir.model.access.csv",
        "report/account_asset_transfer_report.xml",
        "views/account_asset_transfer_type.xml",
         "views/account_asset_transfer.xml",
        "views/menuitem.xml",
    ],
}
