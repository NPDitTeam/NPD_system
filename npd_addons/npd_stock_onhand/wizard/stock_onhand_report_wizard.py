# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class StockOnhandReportWizard(models.TransientModel):
    _name = "stock.onhand.report.wizard"
    _description = "Stock On Hand Report Wizard"

    date_range_id = fields.Many2one(comodel_name="date.range", string="Period")
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location", required=True
    )
    product_ids = fields.Many2many(
        comodel_name="product.product", string="Products", required=True
    )
    product_cate_id = fields.Many2one('product.category', string='Product Category')

    @api.onchange("date_range_id")
    def _onchange_date_range_id(self):
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.onchange('product_cate_id')
    def _onchange_product_cate_id(self):
        product_ids = self.env["product.product"].search([('categ_id','=', self.product_cate_id.id)])
        self.product_ids = product_ids.ids
        
    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref("npd_stock_onhand.action_report_stock_onhand_report_html")
        # action = self.env.ref("npd_stock_onhand.action_stock_onhand_view")
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        model = self.env["report.stock.onhand.report"]
        report = model.create(self._prepare_stock_onhand_report())
        context["active_id"] = report.id
        context["active_ids"] = report.ids
        vals["context"] = context
        return vals

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)

    def _prepare_stock_onhand_report(self):
        self.ensure_one()
        return {
            "date_from": self.date_from,
            "date_to": self.date_to or fields.Date.context_today(self),
            "product_ids": [(6, 0, self.product_ids.ids)],
            "location_id": self.location_id.id,
        }

    def _export(self, report_type):
        model = self.env["report.stock.onhand.report"]
        report = model.create(self._prepare_stock_onhand_report())
        return report.print_report(report_type)
