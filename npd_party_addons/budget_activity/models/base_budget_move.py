# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BaseBudgetMove(models.AbstractModel):
    _inherit = "base.budget.move"

    activity_id = fields.Many2one(
        comodel_name="budget.activity",
        string="Activity",
        index=True,
    )
    activity_group_id = fields.Many2one(
        comodel_name="budget.activity.group",
        string="Activity Group",
        related="activity_id.activity_group_id",
    )

    @api.constrains("activity_id", "account_id")
    def _check_activity_account(self):
        for rec in self.filtered("activity_id"):
            if rec.account_id != rec.activity_id.account_id:
                raise UserError(
                    _("Account not equal to Activity's Account: %s")
                    % rec.activity_id.account_id.display_name
                )


class BudgetDoclineMixin(models.AbstractModel):
    _inherit = "budget.docline.mixin"

    activity_id = fields.Many2one(
        comodel_name="budget.activity",
        string="Activity",
        index=True,
    )

    def _update_budget_commitment(self, budget_vals, reverse=False):
        budget_vals = super()._update_budget_commitment(
            budget_vals, reverse=reverse
        )
        budget_vals["activity_id"] = self.activity_id.id
        # For case object without account_id (PR/PO), normally account is from
        # product, it should now changed to follow activity.
        # But if account_id is part of object (INV), use whatever is passed-in.
        if "account_id" not in self:
            budget_vals["account_id"] = self["activity_id"].account_id.id
        return budget_vals