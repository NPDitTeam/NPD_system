# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[
            ("budget.control", "Budget Control"),
            ("budget.move.forward", "Budget Carry Forward"),
        ],
        ondelete={
            "budget.control": "cascade",
            "budget.move.forward": "cascade",
        },
    )
