# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD,. PART. (<http://www.ineco.co.th>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# POP-001    2013-07-31    Disable when change partner to change due date too.
# POP-002    2013-08-24    Cancel invoice reset period_id = False
# POP-003    2013-08-27    Add Commission
# POP-004    2013-09-09    Change Manual Post when validate invoice
# POP-005    2014-01-07    Change Date Due in account.invoice

from openerp.osv import fields, osv

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import time
#import pooler
from openerp.tools.translate import _
#from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
#import netsvc

class account_voucher_addline(osv.osv):
    _name = 'account.voucher.addline'
    _columns = {
        'name': fields.char('Description', size=64),
        'account_name': fields.related('account_id','name', type='char', size=128, relation='account.account', store=True, string='Account Name'),
        'account_id': fields.many2one('account.account','Account',required=True),
        'voucher_id': fields.many2one('account.voucher','Voucher'),
        'debit': fields.float('Debit', digits_compute=dp.get_precision('Account')),
        'credit': fields.float('Credit', digits_compute=dp.get_precision('Account')),
    }
    _defaults = {
        'name': '...',
    }

class account_invoice(osv.osv):

    def _find_partner(self, inv):
        '''
        Find the partner for which the accounting entries will be created
        '''
        #if the chosen partner is not a company and has a parent company, use the parent for the journal entries 
        #because you want to invoice 'Agrolait, accounting department' but the journal items are for 'Agrolait'
        part = inv.partner_id
        if part.parent_id and not part.is_company:
            part = part.parent_id
        return part

    def onchange_payment_term_date_invoice(self, cr, uid, ids, payment_term_id, date_invoice):
        res = {}        
        if not date_invoice:
            date_invoice = time.strftime('%Y-%m-%d')
        if not payment_term_id:
            return {'value':{'date_due': date_invoice}} #To make sure the invoice has a due date when no payment term 
        pterm_list = self.pool.get('account.payment.term').compute(cr, uid, payment_term_id, value=1, date_ref=date_invoice)
        if pterm_list:
            pterm_list = [line[0] for line in pterm_list]
            pterm_list.sort()
            res = {'value':{'date_due': pterm_list[-1]}}
#         else:
#             raise osv.except_osv(_('Insufficient Data!'), _('The payment term of supplier does not have a payment term line.'))
        return res
    
    def _get_move_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            id = invoice.id
            res[id] = []
            if not invoice.move_id:
                continue
            data_lines = [x for x in invoice.move_id.line_id]
            partial_ids = []
            for line in data_lines:
#                 ids_line = []
#                 if line.reconcile_id:
#                     ids_line = line.reconcile_id.line_id
#                 elif line.reconcile_partial_id:
#                     ids_line = line.reconcile_partial_id.line_partial_ids
#                 l = map(lambda x: x.id, ids_line)
                partial_ids.append(line.id)
            res[id] =[x for x in partial_ids]
        return res
    
    _inherit = "account.invoice"
    _columns = {
        'account_move_lines':fields.function(_get_move_lines, type='many2many', relation='account.move.line', string='General Ledgers'),                
#         'date_due': fields.date('Due Date', select=True,
#             help="If you use payment terms, the due date will be computed automatically at the generation "\
#                 "of accounting entries. The payment term may compute several due dates, for example 50% now and 50% in one month, but if you want to force a due date, make sure that the payment term is not set on the invoice. If you keep the payment term and the due date empty, it means direct payment."),        
        'bill_due': fields.date('Billing Date', select=True),
        'receipt_due': fields.date('Receipt Date', select=True),
        'partner_delivery_id': fields.many2one('res.partner', 'Delivery Address'),
        'service': fields.boolean('Service'),
        'commission_sale': fields.float('Sale Commission'),
        'commission_other': fields.float('Other Commission'),
        'commission_note': fields.char('Commission Note', size=256),
        'commission_pay': fields.boolean('Pay Commission'),
        'date_due': fields.date('Due Date', select=True,
            help="If you use payment terms, the due date will be computed automatically at the generation "\
                "of accounting entries. The payment term may compute several due dates, for example 50% now and 50% in one month, but if you want to force a due date, make sure that the payment term is not set on the invoice. If you keep the payment term and the due date empty, it means direct payment."),
        'period_tax_id': fields.many2one('account.period', 'Tax Period'),
    }
    _defaults = {
        'service': False,
        'commission_sale': 0.0,
        'commission_other': 0.0,
        'commission_pay': False,
    }
    
    #POP-002
    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        account_move_obj = self.pool.get('account.move')
        invoices = self.read(cr, uid, ids, ['move_id', 'payment_ids'])
        move_ids = [] # ones that we will need to remove
        for i in invoices:
            if i['move_id']:
                move_ids.append(i['move_id'][0])
            if i['payment_ids']:
                account_move_line_obj = self.pool.get('account.move.line')
                pay_ids = account_move_line_obj.browse(cr, uid, i['payment_ids'])
                for move_line in pay_ids:
                    if move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids:
                        raise osv.except_osv(_('Error!'), _('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        # POP-002
        self.write(cr, uid, ids, {'state':'cancel', 'move_id':False, 'period_id': False})
        if move_ids:
            # second, invalidate the move(s)
            account_move_obj.button_cancel(cr, uid, move_ids, context=context)
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            account_move_obj.unlink(cr, uid, move_ids, context=context)
        self._log_event(cr, uid, ids, -1.0, 'Cancel Invoice')
        return True
    
    def action_date_assign(self, cr, uid, ids, *args):
        for inv in self.browse(cr, uid, ids):
            if not inv.date_due:
                res = self.onchange_payment_term_date_invoice(cr, uid, inv.id, inv.payment_term.id, inv.date_invoice)
                if res and res['value']:
                    self.write(cr, uid, [inv.id], res['value'])
            if not inv.bill_due:
                if inv.partner_id and inv.partner_id.billing_payment_id:
                    res = self.onchange_payment_term_date_due(cr, uid, inv.id, inv.partner_id.billing_payment_id.id, inv.date_invoice)
                    if res and res['value']:
                        self.write(cr, uid, [inv.id], res['value'])
        return True

    def onchange_payment_term_date_due(self, cr, uid, ids, payment_term_id, date_invoice):
        res = {}        
        if not date_invoice:
            date_invoice = time.strftime('%Y-%m-%d')
        if not payment_term_id:
            return {'value':{'bill_due': date_invoice}} #To make sure the invoice has a due date when no payment term 
        pterm_list = self.pool.get('account.payment.term').compute(cr, uid, payment_term_id, value=1, date_ref=date_invoice)
        if pterm_list:
            pterm_list = [line[0] for line in pterm_list]
            pterm_list.sort()
            res = {'value':{'bill_due': pterm_list[-1]}}
        else:
            raise osv.except_osv(_('Insufficient Data!'), _('The payment term of supplier does not have a payment term line.'))
        return res

#     def write(self, cr, uid, ids, vals, context=None):
#         if vals.get('date_due',False):
#             for line in self.browse(cr, uid, ids):
#                 if line.partner_id.billing_payment_id:
#                     pterm_list = self.pool.get('account.payment.term').compute(cr, uid, line.partner_id.billing_payment_id.id, value=1, date_ref=vals['date_due'])
#                     if pterm_list:
#                         pterm_list = [line[0] for line in pterm_list]
#                         pterm_list.sort()
#                         vals['bill_due'] = pterm_list[-1]
#         return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False

        opt = [('uid', str(uid))]
        if partner_id:

            opt.insert(0, ('id', partner_id))
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if (p.property_account_receivable.company_id and (p.property_account_receivable.company_id.id != company_id)) and (p.property_account_payable.company_id and (p.property_account_payable.company_id.id != company_id)):
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]

            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
                partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
            else:
                acc_id = p.property_account_payable.id
                partner_payment_term = p.property_supplier_payment_term and p.property_supplier_payment_term.id or False
            fiscal_position = p.property_account_position and p.property_account_position.id or False
            if p.bank_ids:
                bank_id = p.bank_ids[0].id

        result = {'value': {
            'account_id': acc_id,
            'payment_term': partner_payment_term,
            'fiscal_position': fiscal_position
            }
        }

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != partner_payment_term:
            if partner_payment_term:
                to_update = self.onchange_payment_term_date_invoice(
                    cr, uid, ids, partner_payment_term, date_invoice)
                result['value'].update(to_update['value'])
# POP-001                
#             else:
#                 result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            result['value'].update(to_update['value'])
        return result
 
    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines !'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = inv.company_id.currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
                    raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
            acc_id = inv.account_id.id

            name = inv['name'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': inv.date_due or t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')

            part = self._find_partner(inv)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration':inv.comment
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id

            ctx.update(invoice=inv)
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            # POP-004 
            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True

    #Ad
    def invoice_validate(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            if data.period_id and not data.period_tax_id:
                data.write({'period_tax_id': data.period_id.id})
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        return True
    
    def view_entry(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_move_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("View Entry"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
#             'context': {
#                 'default_partner_id': self._find_partner(inv).id,
#                 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
#                 'default_reference': inv.number or inv.name,
#                 'default_name': inv.name,
#                 'close_after_process': True,
#                 'invoice_type': inv.type,
#                 'invoice_id': inv.id,
#                 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
#                 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
#            }
        }  

class account_voucher(osv.osv):
    
    def _get_move_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            id = invoice.id
            res[id] = []
            if not invoice.move_id:
                continue
            data_lines = [x for x in invoice.move_id.line_id]
            partial_ids = []
            for line in data_lines:
#                 ids_line = []
#                 if line.reconcile_id:
#                     ids_line = line.reconcile_id.line_id
#                 elif line.reconcile_partial_id:
#                     ids_line = line.reconcile_partial_id.line_partial_ids
#                 l = map(lambda x: x.id, ids_line)
                partial_ids.append(line.id)
            res[id] =[x for x in partial_ids]
        return res
    _inherit = "account.voucher"
    _columns = {
        'account_move_lines':fields.function(_get_move_lines, type='many2many', 
            relation='account.move.line', string='General Ledgers'),      
        'wht_ids': fields.one2many('ineco.wht', 'voucher_id', 'WHT'),
        'cheque_id': fields.many2one('ineco.cheque','Cheque'),        
        'bill_number': fields.char('Bill/Receipt No', size=63, track_visibility='onchange'),
        'period_tax_id': fields.many2one('account.period', 'Tax Period'),
        'account_model_id': fields.many2one('account.model', 'Model'),
        'addline_ids': fields.one2many('account.voucher.addline','voucher_id','Add Line'),
        'cheque_ids': fields.many2many('ineco.cheque', 'voucher_cheque_ids', 'voucher_id', 'cheque_id', 'Cheque'),      
    }

    def button_loadtemplate(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            if data.account_model_id:
                for line in data.account_model_id.lines_id:
                    addline = self.pool.get('account.voucher.addline')
                    addline.create(cr, uid, {
                        'account_id': line.account_id.id,
                        'name': line.name,
                        'debit': line.debit,
                        'credit': line.credit,
                        'voucher_id': data.id,
                    })
        #self.write(cr, uid, ids, {'state':'approve'})
        return True
    
    def _get_wht_total(self, cr, uid, voucher_id, context=None):
        _amount_tax = 0.0
        voucher = self.browse(cr, uid, voucher_id)
        for wht in voucher.wht_ids:
            _amount_tax += wht.tax or 0.0
        return round(_amount_tax, 2)

    def _get_template_debit_total(self, cr, uid, voucher_id, context=None):
        _amount_tax = 0.0
        voucher = self.browse(cr, uid, voucher_id)
        for wht in voucher.addline_ids:
            _amount_tax += wht.debit or 0.0
        return round(_amount_tax, 2)

    def _get_template_credit_total(self, cr, uid, voucher_id, context=None):
        _amount_tax = 0.0
        voucher = self.browse(cr, uid, voucher_id)
        for wht in voucher.addline_ids:
            _amount_tax += wht.credit or 0.0
        return round(_amount_tax, 2)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}           
        default.update({
            'wht_ids':False,
        })
        return super(account_voucher, self).copy(cr, uid, id, default, context)

    def template_move_line_create(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        move_line_pool = self.pool.get('account.move.line')
        for line in voucher_brw.addline_ids:
            debit = credit = 0.0
            debit = line.debit
            credit = line.credit 
            if debit < 0: credit = -debit; debit = 0.0
            if credit < 0: debit = -credit; credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            #set the first line of the voucher
            move_line = {
                    'name': line.name or line.account_name or '/',
                    'debit': debit,
                    'credit': credit,
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'journal_id': voucher_brw.journal_id.id,
                    'period_id': voucher_brw.period_id.id,
                    'partner_id': voucher_brw.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                    'date': voucher_brw.date,
                    'date_maturity': voucher_brw.date_due
                }
            move_line_pool.create(cr, uid, move_line)
        return True

    def wht_move_line_create(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        move_line_pool = self.pool.get('account.move.line')
        for wht in voucher_brw.wht_ids:
            debit = credit = 0.0
            if voucher_brw.type in ('purchase', 'payment'):
                credit = wht.tax
            elif voucher_brw.type in ('sale', 'receipt'):
                debit = wht.tax
            if debit < 0: credit = -debit; debit = 0.0
            if credit < 0: debit = -credit; credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            #set the first line of the voucher
            move_line = {
                    'name': 'WHT NO: ' + wht.name or '/',
                    'debit': debit,
                    'credit': credit,
                    'account_id': wht.account_id.id,
                    'move_id': move_id,
                    'journal_id': voucher_brw.journal_id.id,
                    'period_id': voucher_brw.period_id.id,
                    'partner_id': voucher_brw.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                    'date': voucher_brw.date,
                    'date_maturity': voucher_brw.date_due
                }
            move_line_pool.create(cr, uid, move_line)
        return True
    
    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        account_id = voucher_brw.account_id.id
        debit = credit = 0.0
        if voucher_brw.type in ('purchase', 'payment'):
            credit = voucher_brw.paid_amount_in_company_currency
            credit -= self._get_wht_total(cr, uid, voucher_id, context) or 0.0
            account_id = voucher_brw.journal_id.default_credit_account_id.id
        elif voucher_brw.type in ('sale', 'receipt'):
            debit = voucher_brw.paid_amount_in_company_currency
            debit -= self._get_wht_total(cr, uid, voucher_id, context) or 0.0
            account_id = voucher_brw.journal_id.default_debit_account_id.id
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        move_line = {
                'name': voucher_brw.name or voucher_brw.account_id.name or '/',
                'debit': debit,
                'credit': credit,
                #'account_id': voucher_brw.account_id.id,
                'account_id': account_id,
                'move_id': move_id,
                'journal_id': voucher_brw.journal_id.id,
                'period_id': voucher_brw.period_id.id,
                'partner_id': voucher_brw.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                'date': voucher_brw.date,
                'date_maturity': voucher_brw.date_due
            }
        return move_line
    
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            ######
            # Create the account move record.
            try:
                move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
                # Get the name of the account_move just created
                name = move_pool.browse(cr, uid, move_id, context=context).name
                # Create the first line of the voucher
                move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
                move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
                
                #WHT Tax Amount
                wht_total = self._get_wht_total(cr, uid, voucher.id, context)
                if voucher.type in {'sale','receipt'}:
                    line_total = move_line_brw.debit - move_line_brw.credit + wht_total
                elif voucher.type in {'purchase','payment'}:
                    line_total = move_line_brw.debit - move_line_brw.credit - wht_total
                else:
                    line_total = move_line_brw.debit - move_line_brw.credit
                if wht_total:
                    self.wht_move_line_create(cr, uid, voucher.id, move_id, company_currency, current_currency, context)
                    
                #Create Template Move Line    
                if voucher.addline_ids and voucher.payment_option == 'without_writeoff':
                    self.template_move_line_create(cr, uid, voucher.id, move_id, company_currency, current_currency, context)
                template_debit = self._get_template_debit_total(cr, uid, voucher.id, context)
                template_credit = self._get_template_credit_total(cr, uid, voucher.id, context)
                
                if voucher.payment_option == 'without_writeoff':
                    line_total = (move_line_brw.debit + template_debit) - (move_line_brw.credit + template_credit)
                    
                rec_list_ids = []
                if voucher.type == 'sale':
                    line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
                elif voucher.type == 'purchase':
                    line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
                
                # Create one move line per voucher line where amount is not 0.0
                line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
    
                if wht_total:
                    if voucher.type in {'purchase','payment'}:
                        line_total = round(line_total,4) - round(wht_total,4)
                    elif voucher.type in {'sale','receipt'}: 
                        line_total = round(line_total,4) + round(wht_total,4)
                
                if voucher.payment_option == 'without_writeoff' and round(line_total,4):
                    raise osv.except_osv('Unreconciled', 'Please input data in template tab to balance debit and credit.')
                
                # Create the writeoff line if needed
                ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
                if ml_writeoff:
                    move_line_pool.create(cr, uid, ml_writeoff, context)
                # We post the voucher.
                self.write(cr, uid, [voucher.id], {
                    'move_id': move_id,
                    'state': 'posted',
                    'number': name,
                })
                if voucher.journal_id.entry_posted:
                    move_pool.post(cr, uid, [move_id], context={})
                # We automatically reconcile the account move lines.
                reconcile = False
                for rec_ids in rec_list_ids:
                    if len(rec_ids) >= 2:
                        reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
            except:
                cr.rollback()
                raise osv.except_osv('Error', 'Validation error please contact administrator.')
        return True

class account_payment_term(osv.osv):
    _inherit = "account.payment.term"
    _columns = {
        'billing_term': fields.boolean('Billing Term'),
    }
    _defaults = {
        'billing_term': False,
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: