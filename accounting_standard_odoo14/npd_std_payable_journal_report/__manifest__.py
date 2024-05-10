{
    "name": "NPD: Payable Journal Report",
    "summary": """Payable Journal report""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "development_status": "Beta",
    "author": "NPD",
    'website': 'https://npd9.com/',
    "depends": ["account"],
    'support': '',
    "data": [
        'security/ir.model.access.csv',
        'data/paper_format.xml',
        'reports/payable_journal.xml',
        'views/report_views.xml',
    ],
    "installable": True,
}
