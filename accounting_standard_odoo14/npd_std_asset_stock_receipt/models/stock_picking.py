from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tests.common import Form


class StockPacking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        super(StockPacking, self)._action_done()
        for move in self:
            for aml in move.move_line_ids_without_package.filtered("asset_profile_id"):
                depreciation_base = 0
                qty = aml.qty_done
                i = 0
                while i < qty:
                    vals = {
                        "name": aml.product_id.name,
                        "code": move.name,
                        "profile_id": aml.asset_profile_id,
                        "purchase_value": depreciation_base,
                        "date_start": move.date_done or fields.Date.today(),
                    }
                    if self.env.context.get("company_id"):
                        vals["company_id"] = self.env["res.company"].browse(
                            self.env.context["company_id"]
                        )
                    asset_form = Form(
                        self.env["account.asset"].with_context(
                            create_asset_from_move_line=True
                        )
                    )
                    for key, val in vals.items():
                        setattr(asset_form, key, val)
                    asset = asset_form.save()
                    if aml.asset_group_id:
                        asset.write({"group_ids": [aml.asset_group_id.id]})
                    if aml.warranty_date_end:
                        self.env["account.asset.insurance"].create(
                            {
                                'insurance_id':asset.id,
                                'end_of_warranty':aml.warranty_date_end
                            })
                    i += 1
            for aml in move.move_ids_without_package.filtered("asset_profile_id"):
                depreciation_base = 0
                qty = aml.product_uom_qty
                i = 0
                while i < qty:
                    vals = {
                        "name": aml.product_id.name,
                        "code": move.name,
                        "profile_id": aml.asset_profile_id,
                        "purchase_value": depreciation_base,
                        "date_start": move.date_done or fields.Date.today(),
                    }
                    if self.env.context.get("company_id"):
                        vals["company_id"] = self.env["res.company"].browse(
                            self.env.context["company_id"]
                        )
                    asset_form = Form(
                        self.env["account.asset"].with_context(
                            create_asset_from_move_line=True
                        )
                    )
                    for key, val in vals.items():
                        setattr(asset_form, key, val)
                    asset = asset_form.save()
                    if aml.asset_group_id:
                        asset.write({"group_ids": [aml.asset_group_id.id]})
                    if aml.warranty_date_end:
                         self.env["account.asset.insurance"].create(
                            {
                                'insurance_id':asset.id,
                                'end_of_warranty':aml.warranty_date_end
                            })
                    i += 1

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    asset_group_id = fields.Many2one(
        comodel_name="account.asset.group",
        string="Asset Group",
        required=False,
    )
    asset_profile_id = fields.Many2one(
        comodel_name="account.asset.profile",
        string="Asset Profile",
        required=False,
    )

class StockMove(models.Model):
    _inherit = "stock.move"

    asset_group_id = fields.Many2one(
        comodel_name="account.asset.group",
        string="Asset Group",
        required=False,
    )
    asset_profile_id = fields.Many2one(
        comodel_name="account.asset.profile",
        string="Asset Profile",
        required=False,
    )
    warranty_date_end = fields.Date('End of Warranty')