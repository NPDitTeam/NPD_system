# -*- coding: utf-8 -*-


from odoo import api, models, _
import logging

_logger = logging.getLogger(__name__)


class ReportWithholding(models.AbstractModel):
    _name = 'report.npd_npd_pnd_qweb.report_withholding'
    _description = 'Report Withholding'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('npd_npd_pnd_qweb.report_withholding')
        records = self.env['withholding.tax.cert'].browse(docids)

        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': records,
            'data': data,

        }
