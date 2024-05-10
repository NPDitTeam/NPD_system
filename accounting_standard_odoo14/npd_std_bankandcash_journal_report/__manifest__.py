{
    "name": "NPD: Bank and Cash Journal Report",
    "summary": """Bank and Cash Journal report""",
    "version": "14.0.1.0.2",
    "license": "AGPL-3",
    "development_status": "Beta",
    "author": "npd",
    'website': '',
    "depends": ["account"],
    'support': '',
    "data": [
        'security/ir.model.access.csv',
        'data/paper_format.xml',
        'reports/bankandcash_journal.xml',
        'views/report_views.xml',
    ],
    "installable": True,
}
