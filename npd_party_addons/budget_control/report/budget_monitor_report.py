# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BudgetMonitorReport(models.Model):
    _name = "budget.monitor.report"
    _description = "Budget Monitoring Report"
    _auto = False
    _order = "date desc"
    _rec_name = "reference"

    res_id = fields.Reference(
        selection=lambda self: [("mis.budget.item", "Budget Item")]
        + self._get_budget_docline_model(),
        string="Resource ID",
    )
    reference = fields.Char()
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
    )
    analytic_group = fields.Many2one(
        comodel_name="account.analytic.group",
    )
    date = fields.Date()
    amount = fields.Float()
    amount_type = fields.Selection(
        selection=lambda self: [("1_budget", "Budget")]
        + self._get_budget_amount_type(),
        string="Type",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
    )
    date_range_id = fields.Many2one(
        comodel_name="date.range",
    )
    budget_period_id = fields.Many2one(
        comodel_name="budget.period",
    )
    budget_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submit", "Submitted"),
            ("done", "Controlled"),
            ("cancel", "Cancelled"),
        ],
        string="Budget State",
    )
    active = fields.Boolean()

    @property
    def _table_query(self):
        return """
            select a.*, d.id as date_range_id, p.id as budget_period_id
            from ({}) a
            left outer join date_range d
                on a.date between d.date_start and d.date_end
            left outer join budget_period p
                on a.date between p.bm_date_from and p.bm_date_to
            {}
        """.format(
            self._get_sql(), self._get_where_sql()
        )

    def _get_consumed_sources(self):
        return [
            {
                "model": ("account.move.line", "Account Move Line"),
                "type": ("8_actual", "Actual"),
                "budget_move": ("account_budget_move", "move_line_id"),
                "source_doc": ("account_move", "move_id"),
            }
        ]

    def _get_budget_docline_model(self):
        """ Return list of all res_id models selection """
        return [x["model"] for x in self._get_consumed_sources()]

    def _get_budget_amount_type(self):
        """ Return list of all amount_type selection """
        return [x["type"] for x in self._get_consumed_sources()]

    def _get_select_amount_types(self):
        sql_select = {}
        for source in self._get_consumed_sources():
            res_model = source["model"][0]  # i.e., account.move.line
            amount_type = source["type"][0]  # i.e., 8_actual
            res_field = source["budget_move"][1]  # i.e., move_line_id
            sql_select[amount_type] = {
                0: """
                %s000000000 + a.id as id,
                '%s,' || a.%s as res_id,
                a.analytic_account_id,
                a.analytic_group,
                a.date as date,
                '%s' as amount_type,
                a.credit-a.debit as amount,
                a.product_id,
                a.account_id,
                b.name as reference,
                null::char as budget_state,
                1::boolean as active
                """
                % (amount_type[:1], res_model, res_field, amount_type)
            }
        return sql_select

    def _get_from_amount_types(self):
        sql_from = {}
        for source in self._get_consumed_sources():
            budget_table = source["budget_move"][
                0
            ]  # i.e., account_budget_move
            doc_table = source["source_doc"][0]  # i.e., account_move
            doc_field = source["source_doc"][1]  # i.e., move_id
            amount_type = source["type"][0]  # i.e., 8_actual
            sql_from[
                amount_type
            ] = """
                from {} a
                left outer join {} b on a.{} = b.id
            """.format(
                budget_table,
                doc_table,
                doc_field,
            )
        return sql_from

    def _select_budget(self):
        return {
            0: """
            1000000000 + a.id as id,
            'mis.budget.item,' || a.id as res_id,
            a.analytic_account_id,
            b.analytic_group,
            a.date_to as date,  -- approx date
            '1_budget' as amount_type,
            a.amount as amount,
            null::integer as product_id,
            null::integer as account_id,
            b.name as reference,
            b.state as budget_state,
            a.active as active
        """
        }

    def _from_budget(self):
        return """
            from mis_budget_item a
            left outer join budget_control b on a.budget_control_id = b.id
        """

    def _where_budget(self):
        return ""
        # return """ where a.active = true """

    def _select_statement(self, amount_type):
        return self._get_select_amount_types()[amount_type]

    def _from_statement(self, amount_type):
        return self._get_from_amount_types()[amount_type]

    def _where_actual(self):
        return """
            where b.state = 'posted'
        """

    def _get_sql(self):
        select_budget_query = self._select_budget()
        key_select_budget_list = sorted(select_budget_query.keys())
        select_budget = ", ".join(
            select_budget_query[x] for x in key_select_budget_list
        )
        select_actual_query = self._select_statement("8_actual")
        key_select_actual_list = sorted(select_budget_query.keys())
        select_actual = ", ".join(
            select_actual_query[x] for x in key_select_actual_list
        )
        return "(select {} {} {}) union (select {} {} {})".format(
            select_budget,
            self._from_budget(),
            self._where_budget(),
            select_actual,
            self._from_statement("8_actual"),
            self._where_actual(),
        )

    def _get_where_sql(self):
        return ""