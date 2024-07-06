import requests
from odoo import api, fields, models, _
from datetime import datetime
import logging
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)


class ApprovalRequest(models.Model):
    _name = "approval.request"
    _inherit = ['mail.thread']
    _description = "Approval Request"

    name = fields.Char(string="Title")
    request_date = fields.Datetime(string="Request Date", default=datetime.today())
    product_id = fields.Many2one("product.template", string="Item")
    amount = fields.Float(string="Amount")
    approval_name_id = fields.Many2one("approval.type", string="Type", required=True)
    payment = fields.Float(string="Payment")
    description = fields.Html(string="Description")
    approver_ids = fields.Many2many('res.users', string='Approvers')
    request_by = fields.Many2one("res.users", string="Request By", default=lambda self: self.env.user, readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submitted'), ('approve', 'Approved'), ('cancel', 'Cancel')],
        string="Status", default="draft", tracking=True, index=True)
    my_approval_ids = fields.One2many('my.approval', 'request_id', string='Approvals')
    date_from = fields.Datetime('From Date')
    date_to = fields.Datetime('To Date')
    location = fields.Char(string="Location")
    quality = fields.Char(string="Quality")
    period = fields.Float(string="Period")
    contact_number = fields.Char(string="Contact Number")
    contact_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                      string="Contact Status", default="none", compute="_compute_approval_type_field")
    date_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                   string="Date Status", default="none", compute="_compute_approval_type_field")
    period_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                     string="Period Status", default="none", compute="_compute_approval_type_field")
    item_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                   string="Item Status", default="none", compute="_compute_approval_type_field")
    quality_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                      string="Quality Status", default="none", compute="_compute_approval_type_field")
    amount_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                     string="Amount Status", default="none", compute="_compute_approval_type_field")
    payment_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                      string="Payment Status", default="none", compute="_compute_approval_type_field")
    location_status = fields.Selection([('required', 'Required'), ('optional', 'Optional'), ('none', 'None')],
                                       string="Location Status", default="none", compute="_compute_approval_type_field")

    @api.onchange('approval_name_id')
    @api.depends('approval_name_id')
    def _compute_approval_type_field(self):
        for record in self:
            if record.approval_name_id:
                record.contact_status = record.approval_name_id.contact_status
                record.date_status = record.approval_name_id.date_status
                record.period_status = record.approval_name_id.period_status
                record.item_status = record.approval_name_id.item_status
                record.quality_status = record.approval_name_id.quality_status
                record.amount_status = record.approval_name_id.amount_status
                record.payment_status = record.approval_name_id.payment_status
                record.location_status = record.approval_name_id.location_status

    def action_submit(self):
        final_dict = {}
        for record in self:
            record.state = 'submit'
            final_dict = {
                'name': record.name,
                'request_by': record.request_by.id,
                'approval_name_id': record.approval_name_id.id,
                'payment': record.payment,
                'request_date': record.request_date,
                'product_id': record.product_id.id,
                'description': record.description,
                'state': 'submit',
                'request_id': record.id,
            }
            if record.approval_name_id and record.approval_name_id.line_ids:
                final_dict['user_ids'] = [
                    (4, i) for i in record.approval_name_id.line_ids.mapped('user_id').ids]
            self.env['my.approval'].create(final_dict)
            self.send_line_notify(record)

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def set_draft(self):
        for record in self:
            record.state = 'draft'

    def send_line_notify(self, record):
        if not isinstance(record, self.__class__):
            raise ValueError("Expected record to be an instance of %s" % self.__class__)

        url = "https://notify-api.line.me/api/notify"
        token = "18IHqGEsPk7qQ3AMjf1DCkQW9C1f9yizZUenjNAB7oE"  # ใส่ access token ของคุณที่นี่
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # ดึงข้อมูลผู้อนุมัติทั้งหมด
        approvers = ', '.join(record.approval_name_id.line_ids.mapped('user_id.name'))

        # ลบ HTML tags ออกจาก description
        plain_description = BeautifulSoup(record.description or "", "html.parser").get_text()

        message = (
            f"Approval request submitted: {record.name}\n"
            f"Requested by: {record.request_by.name}\n"
            f"Request Date: {record.request_date}\n"
            # f"Amount: {record.amount}\n"
            f"Description: {plain_description}\n"
            # f"Contact: {record.contact_status}\n"
            # f"Date: {record.date_status}\n"
            # f"Period: {record.period_status}\n"
            # f"Item: {record.item_status}\n"
            # f"Quality: {record.quality_status}\n"
            # f"Payment: {record.payment_status}\n"
        
            f"Approvers: {approvers}"
            # f"Location Approval: {record.location}\n"
        )

        payload = {'message': message}
        response = requests.post(url, headers=headers, data=payload)

        # ใช้ print เพื่อแสดงสถานะการตอบกลับ
        if response.status_code == 200:
            print('LINE notification sent successfully. Response:', response.text)
            return True
        else:
            print('Failed to send LINE notification. Response:', response.text)
            return False
