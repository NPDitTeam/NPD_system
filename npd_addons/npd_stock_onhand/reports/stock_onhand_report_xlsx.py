# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

_logger = logging.getLogger(__name__)


class ReportStockOnhandReportXlsx(models.AbstractModel):
    _name = "npd_stock_onhand.report_stock_onhand_report_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        for product in objects.product_ids:
            for ws_params in self._get_ws_params(workbook, data, product):
                ws_name = ws_params.get("ws_name")
                ws_name = self._check_ws_name(ws_name)
                ws = workbook.add_worksheet(ws_name)
                generate_ws_method = getattr(self, ws_params["generate_ws_method"])
                generate_ws_method(workbook, ws, ws_params, data, objects, product)

    def _get_ws_params(self, wb, data, product):
        filter_template = {
            "1_date_from": {
                "header": {"value": "Date from"},
                "data": {
                    "value": self._render("date_from"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "2_date_to": {
                "header": {"value": "Date to"},
                "data": {
                    "value": self._render("date_to"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "3_location": {
                "header": {"value": "Location"},
                "data": {
                    "value": self._render("location"),
                    "format": FORMATS["format_tcell_center"],
                },
            },
        }
        initial_template = {
            "1_ref": {
                "data": {"value": "Initial", "format": FORMATS["format_tcell_center"]},
                "colspan": 4,
            },
            "2_balance": {
                "data": {
                    "value": self._render("balance"),
                    "format": FORMATS["format_tcell_amount_right"],
                }
            },
        }
        stock_onhand_template = {
            "0_line_number": {
                "header": {"value": "line_number"},
                "data": {
                    "value": self._render("line_number"),},
                "width": 5,
            },
            "1_lot": {
                "header": {"value": "Lot"},
                "data": {
                    "value": self._render("lot"),
                   
                },
                "width": 25,
            },
            "2_date": {
                "header": {"value": "Date"},
                "data": {
                    "value": self._render("date"),
                    "format": FORMATS["format_tcell_date_left"],
                },
                "width": 25,
            },
            "3_product_code": {
                "header": {"value": "Product Code"},
                "data": {"value": self._render("product_code")},
                "width": 25,
            },
            "4_product": {
                "header": {"value": "Product"},
                "data": {"value": self._render("product")},
                "width": 25,
            },
            "5_balance": {
                "header": {"value": "Balance Qty"},
                "data": {"value": self._render("balance")},
                "width": 25,
            },
            "6_product_uom": {
                "header": {"value": "Product Uom"},
                "data": {"value": self._render("product_uom")},
                "width": 25,
            },
            "7_secondary_qty": {
                "header": {"value": "Secondary Qty"},
                "data": {"value": self._render("secondary_qty")},
                "width": 25,
            },
            "8_secondary_uom": {
                "header": {"value": "Secondary Uom"},
                "data": {"value": self._render("secondary_uom")},
                "width": 25,
            },
            "9_total_value": {
                "header": {"value": "Total Value"},
                "data": {"value": self._render("total_value")},
                "width": 25,
            },
        }

        ws_params = {
            "ws_name": product.name,
            "generate_ws_method": "_stock_onhand_report",
            "title": "Stock Card - {}".format(product.name),
            "wanted_list_filter": [k for k in sorted(filter_template.keys())],
            "col_specs_filter": filter_template,
            "wanted_list_initial": [k for k in sorted(initial_template.keys())],
            "col_specs_initial": initial_template,
            "wanted_list": [k for k in sorted(stock_onhand_template.keys())],
            "col_specs": stock_onhand_template,
        }
        return [ws_params]

    def _stock_onhand_report(self, wb, ws, ws_params, data, objects, product):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])
        self._set_column_width(ws, ws_params)
        # Title
        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)
        # Filter Table
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_blue_center"],
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={
                "date_from": objects.date_from or "",
                "date_to": objects.date_to or "",
                "location": objects.location_id.display_name or "",
            },
            col_specs="col_specs_filter",
            wanted_list="wanted_list_filter",
        )
        row_pos += 1
        # Stock Card Table
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=FORMATS["format_theader_blue_center"],
        )
        ws.freeze_panes(row_pos, 0)
        balance = objects._get_initial(
            objects.results.filtered(lambda l: l.product_id == product and l.is_initial)
        )
        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="data",
            render_space={"balance": balance},
            col_specs="col_specs_initial",
            wanted_list="wanted_list_initial",
        )
        product_lines = objects.results.filtered(
            lambda l: l.product_id == product and not l.is_initial
        )
        line_number = 0
        for line in product_lines:
            balance = line.product_in - line.product_out
            lot_secondary_balance = line.secondary_quantity_in - line.secondary_quantity_out
            total_value = line.value * balance
            line_number += 1
            row_pos = self._write_line(
                ws,
                row_pos,
                ws_params,
                col_specs_section="data",
                render_space={
                    "line_number": line_number,
                    "lot": line.lot_id.name,
                    "date": "",
                    "product": line.product_id.name or "",
                    "product_code": line.product_id.default_code or "",
                    "balance": balance or 0,
                    "product_uom": line.product_uom.name or "", 
                    "secondary_qty": lot_secondary_balance or 0,
                    "secondary_uom": line.product_id.secondary_uom_id.name or "",
                     "total_value": total_value or 0,
                },
                default_format=FORMATS["format_tcell_amount_right"],
            )
