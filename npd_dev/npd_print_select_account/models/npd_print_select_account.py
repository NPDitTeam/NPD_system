
from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    document_type = fields.Selection([
        ('invoice', 'ใบแจ้งหนี้'),
        ('tax_invoice', 'ใบกำกับภาษี'),
        ('delivery_note', 'ใบส่งสินค้า'),
    ], string='Document Type', default='invoice')