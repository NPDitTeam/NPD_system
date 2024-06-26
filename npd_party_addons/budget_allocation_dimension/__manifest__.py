# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Budget Allocation Dimension",
    "summary": "Allocate budget by dimension",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-budgeting",
    "depends": [
        "analytic_tag_dimension_enhanced",
        "budget_allocation",
    ],
    "data": [
        "views/analytic_view.xml",
        "views/account_move_view.xml",
        "views/budget_allocation_view.xml",
        "views/budget_control_view.xml",
    ],
    "installable": True,
}
