# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HRExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    advance_budget_move_ids = fields.One2many(
        comodel_name="advance.budget.move",
        inverse_name="sheet_id",
    )

    def action_submit_sheet(self):
        self._check_analtyic_advance()
        return super().action_submit_sheet()

    def _check_analtyic_advance(self):
        """ To clear advance, analytic must equal to the clear advance's """
        for sheet in self.filtered("advance_sheet_id"):
            advance = sheet.advance_sheet_id
            adv_analytic = advance.expense_line_ids.mapped(
                "analytic_account_id"
            )
            if (
                sheet.expense_line_ids.mapped("analytic_account_id")
                != adv_analytic
            ):
                raise UserError(
                    _(
                        "All selected analytic must equal to its clearing advance: %s"
                    )
                    % adv_analytic.display_name
                )

    def write(self, vals):
        """ Clearing for its Advance """
        res = super().write(vals)
        if vals.get("state") in ("approve", "cancel"):
            clearings = self.filtered("advance_sheet_id")
            clearings.mapped("expense_line_ids").uncommit_advance_budget()
        return res


class HRExpense(models.Model):
    _inherit = "hr.expense"

    advance_budget_move_ids = fields.One2many(
        comodel_name="advance.budget.move",
        inverse_name="expense_id",
    )

    def _filter_current_move(self, analytic):
        self.ensure_one()
        if self._context.get("advance", False):
            return self.advance_budget_move_ids.filtered(
                lambda l: l.analytic_account_id == analytic
            )
        return super()._filter_current_move(analytic)

    @api.depends("advance_budget_move_ids", "budget_move_ids")
    def _compute_commit(self):
        advances = self.filtered("advance")
        expenses = self - advances
        # Advances
        for rec in self:
            debit = sum(rec.advance_budget_move_ids.mapped("debit"))
            credit = sum(rec.advance_budget_move_ids.mapped("credit"))
            rec.amount_commit = debit - credit
            if rec.advance_budget_move_ids:
                rec.date_commit = min(
                    rec.advance_budget_move_ids.mapped("date")
                )
            else:
                rec.date_commit = False
        # Expenses
        super(HRExpense, expenses)._compute_commit()

    def _get_account_move_by_sheet(self):
        # When advance create move, do set not_affect_budget = True
        move_grouped_by_sheet = super()._get_account_move_by_sheet()
        for sheet in self.mapped("sheet_id").filtered("advance"):
            move_grouped_by_sheet[sheet.id].not_affect_budget = True
        return move_grouped_by_sheet

    def recompute_budget_move(self):
        # Expenses
        expenses = self.filtered(lambda l: not l.advance)
        super(HRExpense, expenses).recompute_budget_move()
        # Advances
        advances = self.filtered(lambda l: l.advance).with_context(
            alt_budget_move_model="advance.budget.move",
            alt_budget_move_field="advance_budget_move_ids",
        )
        super(HRExpense, advances).recompute_budget_move()
        # If the advances has any clearing, uncommit them from advance
        adv_sheets = advances.mapped("sheet_id")
        clearings = self.search(
            [("sheet_id.advance_sheet_id", "in", adv_sheets.ids)]
        )
        clearings.uncommit_advance_budget()

    def close_budget_move(self):
        # Expenses
        expenses = self.filtered(lambda l: not l.advance)
        super(HRExpense, expenses).close_budget_move()
        # Advances)
        advances = self.filtered(lambda l: l.advance).with_context(
            alt_budget_move_model="advance.budget.move",
            alt_budget_move_field="advance_budget_move_ids",
        )
        super(HRExpense, advances).close_budget_move()

    def commit_budget(self, reverse=False, **vals):
        if self.advance:
            self = self.with_context(
                alt_budget_move_model="advance.budget.move",
                alt_budget_move_field="advance_budget_move_ids",
            )
        return super().commit_budget(reverse=reverse, **vals)

    def uncommit_advance_budget(self):
        """For clearing in valid state, do uncommit for related Advance."""
        budget_moves = self.env["advance.budget.move"]
        for clearing in self.filtered("can_commit"):
            cl_state = clearing.sheet_id.state
            if self.env.context.get("force_commit") or cl_state in (
                "approve",
                "done",
            ):
                # !!! There is no direct reference between advance and clearing !!!
                advance = clearing.sheet_id.advance_sheet_id.expense_line_ids
                advance.ensure_one()
                clearing_amount = (
                    clearing.total_amount
                    if self.env.company.budget_include_tax
                    else clearing.untaxed_amount
                )
                budget_move = advance.with_context(
                    uncommit=True
                ).commit_budget(
                    reverse=True,
                    clearing_id=clearing.id,
                    amount_currency=clearing_amount,
                )
                budget_moves |= budget_move
            else:
                # Cancel or draft, not commitment line
                self.env["advance.budget.move"].search(
                    [("clearing_id", "=", clearing.id)]
                ).unlink()
        return budget_moves