{
    "name": "NPD Standard : Create Cheque",
    "summary": """Create Cheque""",
    "version": "14.0.2",
    "license": "AGPL-3",
    "development_status": "Beta",
    "author": "npd",
    'website': 'https://npd9.com/',
    "depends": ["account_cheque"],
    "data": [
        'security/ir.model.access.csv',
        "wizard/account_create_cheque_view.xml",
        "views/account_cheque.xml",
    ],
    "installable": True,
}
