from odoo import api, models, fields, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class npdVoucherQweb(models.Model):
    _name = "npd.voucher.qweb"

    move_id = fields.Many2one('account.move', )
    journal_id = fields.Char(string='Journal')
    name = fields.Char()
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    account_analytic_account = fields.Char()
    account_analytic_tag = fields.Char()


class PaymentVoucherForm(models.AbstractModel):
    _name = 'report.npd_std_journal_voucher_qweb.payment_voucher_pdf'

    def _convert_date_to_bhuddhist(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y %H:%M:%S')
        return date_converted

    def _convert_date_to_bhuddhist2(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        i = 0
        ii = 1
        len_doc = len(docs)
        doc_data = {}
        for doc in docs:
            doc_data[i] = {}
            doc_data[i]['date'] = self._convert_date_to_bhuddhist2(doc.date)
            doc_data[i]['current_date'] = self._convert_date_to_bhuddhist(datetime.now() + timedelta(hours=7))
            doc_data[i]['name'] = doc.name
            doc_data[i]['ref'] = doc.ref
            doc_data[i]['narration'] = doc.narration
            doc_data[i]['partner'] = ''
            doc_data[i]['sum_credit'] = 0
            doc_data[i]['sum_debit'] = 0
            doc_data[i]['page'] = 0
            doc_data[i]['line_ids'] = {}
            line_ids_obj = self.env['account.move.line'].search([
                ('move_id', '=', doc.id)
            ], order='debit desc')
            doc_data[i]['analytic_account'] = ''
            for line in line_ids_obj:
                if line.partner_id:
                    doc_data[i]['partner'] = line.partner_id.name
                if line.analytic_account_id.code:
                    if line.account_id.code in doc_data[i]['line_ids']:
                        print('1')
                        if line.analytic_account_id.code in doc_data[i]['line_ids']:
                            print('2')
                            doc_data[i]['line_ids'][line.analytic_account_id.code]['debit'] += line.debit
                            doc_data[i]['line_ids'][line.analytic_account_id.code]['credit'] += line.credit
                        else:
                            print('3')
                            if line.account_id.code in doc_data[i]['line_ids']:
                                print('5')
                                if doc_data[i]['analytic_account'] == line.analytic_account_id.code:
                                    print('51')
                                    doc_data[i]['line_ids'][line.account_id.code]['debit'] += line.debit
                                    doc_data[i]['line_ids'][line.account_id.code]['credit'] += line.credit
                                else:
                                    print('52')
                                    doc_data[i]['line_ids'][line.analytic_account_id.code] = {
                                        'account_code': line.account_id.code,
                                        'name': line.account_id.name,
                                        'analytic_account': line.analytic_account_id.code,
                                        'debit': line.debit,
                                        'credit': line.credit
                                    }
                            else:
                                print('6')
                                doc_data[i]['line_ids'][line.analytic_account_id.code] = {
                                    'account_code': line.account_id.code,
                                    'name': line.account_id.name,
                                    'analytic_account': line.analytic_account_id.code,
                                    'debit': line.debit,
                                    'credit': line.credit
                                }
                    else:
                        print('7')
                        doc_data[i]['line_ids'][line.account_id.code] = {
                            'account_code': line.account_id.code,
                            'name': line.account_id.name,
                            'analytic_account': line.analytic_account_id.code,
                            'debit': line.debit,
                            'credit': line.credit
                        }
                        doc_data[i]['analytic_account'] = line.analytic_account_id.code
                else:
                    print('8')
                    if line.account_id.code in doc_data[i]['line_ids']:
                        print('9')
                        doc_data[i]['line_ids'][line.account_id.code]['debit'] += line.debit
                        doc_data[i]['line_ids'][line.account_id.code]['credit'] += line.credit
                    else:
                        print('10')
                        doc_data[i]['line_ids'][line.account_id.code] = {
                            'account_code': line.account_id.code,
                            'name': line.account_id.name,
                            'analytic_account': line.analytic_account_id.code,
                            'debit': line.debit,
                            'credit': line.credit
                        }
                print(doc_data[i]['line_ids'])
                doc_data[i]['sum_debit'] += line.debit
                doc_data[i]['sum_credit'] += line.credit

            line_payment_obj = self.env['account.payment'].search([
                ('move_id', '=', doc.id)
            ])
            doc_data[i]['group_inv'] = []
            doc_data[i]['group_wt'] = []
            doc_data[i]['group_cheque'] = []
            if line_payment_obj:
                # invoice
                if line_payment_obj.reconciled_invoice_ids:
                    print('invoice')
                    for inv in line_payment_obj.reconciled_invoice_ids:
                        for inv_ids in inv:
                            doc_data[i]['group_inv'].append(inv_ids)
                # Bill
                if line_payment_obj.reconciled_bill_ids:
                    print('Bill')
                    for inv in line_payment_obj.reconciled_bill_ids:
                        for inv_ids in inv:
                            doc_data[i]['group_inv'].append(inv_ids)
                # wt
                if line_payment_obj.wt_cert_ids:
                    for wt in line_payment_obj.wt_cert_ids:
                        for wht_lid in wt.wt_line:
                            doc_data[i]['group_wt'].append(wht_lid)
                # Cheque
                if line_payment_obj.cheque_id:
                    for cheque in line_payment_obj.cheque_id:
                        doc_data[i]['group_cheque'].append(cheque)

            doc_data[i]['header'] = doc.company_id.name
            doc_data[i]['header2'] = 'ใบสำคัญจ่าย'
            doc_data[i]['logo'] = doc.company_id.logo
            doc_data[i]['page'] = ii
            i += 1
            ii += 1
            print(doc_data)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': doc_data,
            'len_doc': len_doc,
        }


class ReceiptVoucherForm(models.AbstractModel):
    _name = 'report.npd_std_journal_voucher_qweb.receipt_voucher_pdf'

    def _convert_date_to_bhuddhist(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y %H:%M:%S')
        return date_converted

    def _convert_date_to_bhuddhist2(self, convert_date):
        date_converted = convert_date + relativedelta(years=543)
        date_converted = date_converted.strftime('%d/%m/%Y')
        return date_converted

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        i = 0
        ii = 1
        len_doc = len(docs)
        doc_data = {}
        for doc in docs:
            doc_data[i] = {}
            doc_data[i]['date'] = self._convert_date_to_bhuddhist2(doc.date)
            doc_data[i]['current_date'] = self._convert_date_to_bhuddhist(datetime.now() + timedelta(hours=7))
            doc_data[i]['name'] = doc.name
            doc_data[i]['ref'] = doc.ref
            doc_data[i]['narration'] = doc.narration
            doc_data[i]['partner'] = ''
            doc_data[i]['sum_credit'] = 0
            doc_data[i]['sum_debit'] = 0
            doc_data[i]['page'] = 0
            doc_data[i]['line_ids'] = {}
            line_ids_obj = self.env['account.move.line'].search([
                ('move_id', '=', doc.id)
            ], order='debit desc')
            doc_data[i]['analytic_account'] = ''
            for line in line_ids_obj:
                if line.partner_id:
                    doc_data[i]['partner'] = line.partner_id.name
                if line.analytic_account_id.code:
                    if line.account_id.code in doc_data[i]['line_ids']:
                        print('1')
                        if line.analytic_account_id.code in doc_data[i]['line_ids']:
                            print('2')
                            doc_data[i]['line_ids'][line.analytic_account_id.code]['debit'] += line.debit
                            doc_data[i]['line_ids'][line.analytic_account_id.code]['credit'] += line.credit
                        else:
                            print('3')
                            if line.account_id.code in doc_data[i]['line_ids']:
                                print('5')
                                if doc_data[i]['analytic_account'] == line.analytic_account_id.code:
                                    print('51')
                                    doc_data[i]['line_ids'][line.account_id.code]['debit'] += line.debit
                                    doc_data[i]['line_ids'][line.account_id.code]['credit'] += line.credit
                                else:
                                    print('52')
                                    doc_data[i]['line_ids'][line.analytic_account_id.code] = {
                                        'account_code': line.account_id.code,
                                        'name': line.account_id.name,
                                        'analytic_account': line.analytic_account_id.code,
                                        'debit': line.debit,
                                        'credit': line.credit
                                    }
                            else:
                                print('6')
                                doc_data[i]['line_ids'][line.analytic_account_id.code] = {
                                    'account_code': line.account_id.code,
                                    'name': line.account_id.name,
                                    'analytic_account': line.analytic_account_id.code,
                                    'debit': line.debit,
                                    'credit': line.credit
                                }
                    else:
                        print('7')
                        doc_data[i]['line_ids'][line.account_id.code] = {
                            'account_code': line.account_id.code,
                            'name': line.account_id.name,
                            'analytic_account': line.analytic_account_id.code,
                            'debit': line.debit,
                            'credit': line.credit
                        }
                        doc_data[i]['analytic_account'] = line.analytic_account_id.code
                else:
                    print('8')
                    if line.account_id.code in doc_data[i]['line_ids']:
                        print('9')
                        doc_data[i]['line_ids'][line.account_id.code]['debit'] += line.debit
                        doc_data[i]['line_ids'][line.account_id.code]['credit'] += line.credit
                    else:
                        print('10')
                        doc_data[i]['line_ids'][line.account_id.code] = {
                            'account_code': line.account_id.code,
                            'name': line.account_id.name,
                            'analytic_account': line.analytic_account_id.code,
                            'debit': line.debit,
                            'credit': line.credit
                        }
                print(doc_data[i]['line_ids'])
                doc_data[i]['sum_debit'] += line.debit
                doc_data[i]['sum_credit'] += line.credit

            line_payment_obj = self.env['account.payment'].search([
                ('move_id', '=', doc.id)
            ])
            doc_data[i]['group_inv'] = []
            doc_data[i]['group_wt'] = []
            doc_data[i]['group_cheque'] = []
            if line_payment_obj:
                # invoice
                if line_payment_obj.reconciled_invoice_ids:
                    print('invoice')
                    for inv in line_payment_obj.reconciled_invoice_ids:
                        for inv_ids in inv:
                            doc_data[i]['group_inv'].append(inv_ids)
                # Bill
                if line_payment_obj.reconciled_bill_ids:
                    print('Bill')
                    for inv in line_payment_obj.reconciled_bill_ids:
                        for inv_ids in inv:
                            doc_data[i]['group_inv'].append(inv_ids)
                # wt
                if line_payment_obj.wt_cert_ids:
                    for wt in line_payment_obj.wt_cert_ids:
                        for wht_lid in wt.wt_line:
                            doc_data[i]['group_wt'].append(wht_lid)
                # Cheque
                if line_payment_obj.cheque_id:
                    for cheque in line_payment_obj.cheque_id:
                        doc_data[i]['group_cheque'].append(cheque)

            doc_data[i]['header'] = doc.company_id.name
            doc_data[i]['header2'] = 'ใบสำคัญรับ'
            doc_data[i]['logo'] = doc.company_id.logo
            doc_data[i]['page'] = ii
            i += 1
            ii += 1
            print(doc_data)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': doc_data,
            'len_doc': len_doc,
        }

