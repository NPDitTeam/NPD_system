{
    'name': 'NPD Standard : Stock Inventory',
    'version': '14.0.1',
    'description': 'Stock Inventory',
    'summary': 'Stock Inventory',
    'author': 'NPD',
    'website': 'https://npd9.com/',
    'license': 'LGPL-3',
    'category': 'stock',
    'depends': [
        'stock',
        'stock_card_report',
    ],
    'data': [
         'views/stock_picking_view.xml',
    ],
    'auto_install': False,
    'application': False,
}
