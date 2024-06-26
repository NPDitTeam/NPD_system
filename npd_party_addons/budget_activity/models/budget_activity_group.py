# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class BudgetActivityGroup(models.Model):
    _name = "budget.activity.group"
    _description = "Budget Activity Group"

    name = fields.Char(
        required=True,
    )
    active = fields.Boolean(default=True)
    activity_ids = fields.One2many(
        comodel_name="budget.activity", inverse_name="activity_group_id"
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        string="Default Account",
        domain=[("deprecated", "=", False)],
    )
