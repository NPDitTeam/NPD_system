# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Budget Plan - Revision",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Keep track of revised by budget plan",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-budgeting",
    "depends": [
        "budget_control_revision",
        "budget_plan",
        "base_revision",
    ],
    "data": ["views/budget_plan_view.xml"],
    "installable": True,
    "maintainers": ["Saran440"],
    "development_status": "Alpha",
    "post_init_hook": "post_init_hook",
}
