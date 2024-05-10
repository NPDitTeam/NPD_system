# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        """Uncommit budget for source contract document."""
        res = super().write(vals)
        if vals.get("state") in ("draft", "posted", "cancel"):
            self.mapped("invoice_line_ids").uncommit_contract_budget()
        return res
