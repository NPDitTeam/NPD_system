from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # related_products_ids = fields.Many2many(
    #     'product.template',
    #     'product_template_rel',
    #     'src_id',
    #     'dest_id',
    #     string='Related Products',
    #     store=True,
    # )

    def update_product_type(self):
        # roduct_count = self.search_count([('name', 'like', '%(R)')])
        # print('*******************',roduct_count)
        products = self.search([('name', 'like', '%(R)')])
        for product in products:
            product.type = 'product'
            product.sale_ok = 'false'
            product.pfb_rent_ok = 'true'

    # @api.depends('related_products_ids')
    # def _compute_related_product_names(self):
    #     for product in self:
    #         print('product.related_products_ids', product.related_products_ids)
    #
    # related_product_names = fields.Char(string='Related Product Names', compute='_compute_related_product_names',
    #                                     store=True)


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     @api.model
#     def create(self, values):
#         line = super(SaleOrderLine, self).create(values)
#
#         if 'product_id' in values and 'order_id' in values:
#             product_id = values['product_id']
#             order_id = values['order_id']
#             order = self.env['sale.order'].browse(order_id)
#
#             related_products_check = self.env['product.product'].search(
#                 [('id', '=', product_id)])
#
#             related_products = self.env['product.product'].search(
#                 [('product_tmpl_id', '=', related_products_check.related_products_ids.ids)])
#
#             new_lines = self.env['sale.order.line']
#             for related_product in related_products:
#
#                 new_line = self.env['sale.order.line'].create({
#                     'order_id': order_id,
#                     'product_id': related_product.id,
#
#                 })
#                 new_lines += new_line
#
#             order.write({'order_line': [(4, line.id) for line in new_lines]})
#
#         return line
