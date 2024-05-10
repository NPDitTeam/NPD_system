from odoo import api, fields, models


class WithholdingTaxCert(models.Model):
    _inherit = 'withholding.tax.cert'

    filter_supplier_branch = fields.Selection([
        ('supplier', 'Supplier'),
        ('branch', 'Branch')
    ], string="Filters Supplier/Branch", default="supplier", store=True)