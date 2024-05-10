{
    'name': 'NPD Standard : Cheque Standard Form Qweb',
    'version': '14.0.1',
    "author": "npd",
    "website": "https://npd9.com/",
    'license': 'AGPL-3',
    'category': 'Report',
    'depends': ['base',
                'web',
                ],
    'data': [
        'data/paper_format.xml',
        'reports/layout.xml',
        'data/report_data.xml',
    ],
    'installable': True,
}
