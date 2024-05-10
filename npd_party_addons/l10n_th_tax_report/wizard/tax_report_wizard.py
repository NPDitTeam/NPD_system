# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval


class TaxReportWizard(models.TransientModel):
    _name = "tax.report.wizard"
    _description = "Wizard for Tax Report"

    # Search Criteria
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        string="Company",
        required=True,
        ondelete="cascade",
    )
    tax_group_id = fields.Many2one(
        comodel_name="account.tax.group",
        string="Tax Group",
        required=True,
    )
    tax_id = fields.Many2many(comodel_name="account.tax",
                              required=True,)

    date_range_id = fields.Many2one(
        comodel_name="date.range", string="Period", required=True
    )

    @api.onchange('tax_group_id')
    def _set_tex_id(self):
        for rec in self:
            rec.tax_id = False
            if rec.tax_group_id:
                tax = rec.env['account.tax'].search([('tax_group_id', '=', rec.tax_group_id.id), ('active', '=', True)])
                if tax:
                    rec.write({'tax_id':  [(6, 0, tax.ids)]})


    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref("l10n_th_tax_report.action_report_tax_report_html")
        vals = action.read()[0]
        context1 = vals.get("context", {})
        if context1:
            context1 = safe_eval(context1)
        model = self.env["report.tax.report"]
        report = model.create(self._prepare_tax_report())
        context1["active_id"] = report.id
        context1["active_ids"] = report.ids
        vals["context"] = context1
        return vals

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)

    def _prepare_tax_report(self):
        self.ensure_one()
        return {
            "company_id": self.company_id.id,
            "tax_id": self.tax_id.ids,
            "date_range_id": self.date_range_id.id,
            "date_from": self.date_range_id.date_start,
            "date_to": self.date_range_id.date_end,
        }

    def _export(self, report_type):
        model = self.env["report.tax.report"]
        report = model.create(self._prepare_tax_report())
        return report.print_report(report_type)
