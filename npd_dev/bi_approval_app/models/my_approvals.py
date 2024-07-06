# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MyApproval(models.Model):
    _name = "my.approval"
    _inherit = ['mail.thread']
    _description = "My Approval"

    name = fields.Char(string="Title")
    request_date = fields.Datetime(string="Request Date")
    product_id = fields.Many2one("product.template", string="Item")
    approved_ids = fields.Many2many(
        "res.users", 'my_approvaled_ref_user_id', string="Approved Users")
    approval_name_id = fields.Many2one("approval.type", string="Type")
    payment = fields.Float(string="Payment")
    description = fields.Html(string="Description")
    request_by = fields.Many2one("res.users",
                                 string="Request By", readonly=True)
    request_id = fields.Many2one('approval.request', string='Request')
    user_ids = fields.Many2many("res.users", string="Approvers")
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'), ('approve', 'Approved'), ('cancel', 'Cancel')], string="Status",
                             default="draft", tracking=True, index=True)
    is_approved = fields.Boolean(
        "is Approved", default=False, compute='_compute_is_approved')

    @api.depends('approved_ids')
    def _compute_is_approved(self):
        for record in self:
            if self.env.user.id in record.approved_ids.ids:
                record.is_approved = True
            else:
                record.is_approved = False

    @api.onchange('approval_name_id')
    def _onchange_approval_name_id(self):
        for record in self:
            if record.approval_name_id and record.approval_name_id.line_ids:
                record.write({'user_ids': [
                    (4, i) for i in record.approval_name_id.line_ids.mapped('user_id').ids]})
            if record.approval_name_id and not record.approval_name_id.line_ids:
                record.write({'user_ids': False})

    def action_approve(self):
        for record in self:
            if record.user_ids:
                if self.env.user.has_group('bi_approval_app.group_approval_manager'):
                    record.approved_ids = record.user_ids.ids
                elif self.env.user.id in record.user_ids.ids and self.env.user.id not in record.approved_ids.ids:
                    record.write(
                        {'approved_ids': [(4, self.env.user.id, None)]})
                elif self.env.user.id in record.user_ids.ids and self.env.user.id in record.approved_ids.ids and not record.user_ids.ids == record.approved_ids.ids:
                    raise ValidationError(
                        _('Already approved and waiting for another approvers'))
                if record.user_ids.ids == record.approved_ids.ids:
                    record.write({'state': 'approve'})
                    if record.request_id:
                        record.request_id.sudo().state = 'approve'
                        template = self.env.ref(
                            'bi_approval_app.email_template_approval_approved')
                        if record.approval_name_id.is_apply_for_model and record.approval_name_id.template_approve_id:
                            mail = template.send_mail(int(record.id))
                            if mail:
                                mail_id = self.env['mail.mail'].browse(mail)
                                mail_id[0].sudo().send()

    def action_refuse(self):
        template = self.env.ref(
            'bi_approval_app.email_template_approval_refuse')
        for record in self:
            record.state = 'cancel'
            final_dict = {
                'state': 'cancel',
            }
            record.request_id.sudo().write(final_dict)
            if record.approval_name_id.is_apply_for_model and record.approval_name_id.template_refuse_id:
                mail = template.send_mail(int(record.id))
                if mail:
                    mail_id = self.env['mail.mail'].browse(mail)
                    mail_id[0].sudo().send()
