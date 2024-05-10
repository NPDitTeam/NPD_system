from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    customer_id = fields.Many2one('res.partner', string='Customer', )

    @api.onchange('customer_id','product_id')
    def onchange_domain_customer_id(self):
        if self.move_id.move_type == 'in_invoice':
            price_list = self.env['product.supplierinfo'].search(
                [ 
                    # ('name', '=', self.move_id.partner_id.id),
                    ('customer_id', '=', self.customer_id.id),
                    ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                ]
                , limit=1
            )
            if price_list:
                self.quantity = price_list.min_qty
                self.price_unit = price_list.price
        