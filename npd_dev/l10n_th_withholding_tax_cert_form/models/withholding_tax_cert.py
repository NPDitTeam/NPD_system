from odoo import models, api


class WithholdingTaxCert(models.Model):
    _inherit = "withholding.tax.cert"

    def _get_report_base_filename(self):
        self.ensure_one()
        return "WT Certificates - %s" % self.display_name

    def _compute_desc_type_other(self, lines, ttype, income_type):
        base_type_other = lines.filtered(
            lambda l: l.wt_cert_income_type in [income_type]
        ).mapped(ttype)
        base_type_other = [x or "" for x in base_type_other]
        desc = ", ".join(base_type_other)
        return desc

    def _group_wt_line(self, lines):
        groups = self.env["withholding.tax.cert.line"].read_group(
            domain=[("id", "in", lines.ids)],
            fields=["wt_cert_income_type", "base", "amount"],
            groupby=["wt_cert_income_type"],
            lazy=False,
        )
        return groups

    def format_number(self, number):
        return '{:,.2f}'.format(number)

    @staticmethod
    def amount_to_text_thai(number):
        units = ["", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
        tens = ["", "สิบ", "ยี่สิบ", "สามสิบ", "สี่สิบ", "ห้าสิบ", "หกสิบ", "เจ็ดสิบ", "แปดสิบ", "เก้าสิบ"]
        thousands = ["", "หนึ่งพัน", "สองพัน", "สามพัน", "สี่พัน", "ห้าพัน", "หกพัน", "เจ็ดพัน", "แปดพัน", "เก้าพัน"]
        hundreds = ["", "หนึ่งร้อย", "สองร้อย", "สามร้อย", "สี่ร้อย", "ห้าร้อย", "หกร้อย", "เจ็ดร้อย", "แปดร้อย", "เก้าร้อย"]
        millions = ["", "หนึ่งล้าน", "สองล้าน", "สามล้าน", "สี่ล้าน", "ห้าล้าน", "หกล้าน", "เจ็ดล้าน", "แปดล้าน", "เก้าล้าน"]

        if number == 0:
            return "ศูนย์บาทถ้วน"

        result = ""
        str_number = "{:.2f}".format(number)
        integer_part, decimal_part = str_number.split(".")

        integer_part = int(integer_part)
        decimal_part = int(decimal_part)

        # แปลงส่วนที่เป็นจำนวนเต็ม
        if integer_part > 0:
            if integer_part >= 1_000_000:
                result += WithholdingTaxCert.amount_to_text_thai(integer_part // 1_000_000) + "ล้าน"
                integer_part %= 1_000_000
            if integer_part >= 100_000:
                result += hundreds[integer_part // 100_000] + "แสน"
                integer_part %= 100_000
            if integer_part >= 10_000:
                result += tens[integer_part // 10_000] + "หมื่น"
                integer_part %= 10_000
            if integer_part >= 1_000:
                result += units[integer_part // 1_000] + "พัน"
                integer_part %= 1_000
            if integer_part >= 100:
                result += hundreds[integer_part // 100]
                integer_part %= 100
            if integer_part >= 10:
                result += tens[integer_part // 10]
                integer_part %= 10
            if integer_part > 0:
                result += units[integer_part]

        result += "บาท"

        # แปลงส่วนที่เป็นทศนิยม
        if decimal_part > 0:
            result += " " + tens[decimal_part // 10] + units[decimal_part % 10] + " สตางค์"
        else:
            result += " ถ้วน"

        return result

    def amount_to_text_custom(self, amount):
        return self.amount_to_text_thai(amount)
