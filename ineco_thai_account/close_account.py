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

from datetime import datetime
from dateutil.relativedelta import relativedelta

import time
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from operator import itemgetter
from openerp.tools.translate import _

class account_period_close(osv.osv_memory):
    _inherit = "account.period.close"
    
    
    def data_save(self, cr, uid, ids, context=None):
        """
        This function close period
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: account period close’s ID or list of IDs
         """
        period_pool = self.pool.get('account.period')
        account_move_obj = self.pool.get('account.move')
        account_account = self.pool.get('account.account')
        ineco_close_accont_obj = self.pool.get('ineco.close.account')
        
        mode = 'done'
        for form in self.read(cr, uid, ids, context=context):
            if form['sure']:
                for id in context['active_ids']:
                    account_move_ids = account_move_obj.search(cr, uid, [('period_id', '=', id), ('state', '=', 'draft')], context=context)
                    if account_move_ids:
                        raise osv.except_osv(_('Invalid Action!'), _('In order to close a period, you must first post related journal entries.'))

                    account_account_ids = account_account.search(cr, uid, [('type', '!=', "view")])
                    account_account_obj = account_account.browse(cr, uid, account_account_ids)
                    for acc_line in account_account_obj:
                        debit = 0.00
                        credit = 0.00
                        before_balance = 0.00
                        balance = 0.00
                        cr.execute('select sum(round(debit,2)) as debit  from account_move_line  where period_id = %s  and account_id = %s',(id,acc_line.id))
                        row_debit =  map(itemgetter(0), cr.fetchall())
                        cr.execute('select sum(round(credit,2)) as credit from account_move_line  where period_id = %s  and account_id = %s',(id,acc_line.id))
                        row_credit = map(itemgetter(0), cr.fetchall())
                        cr.execute('select round(balance,2) from ineco_close_account  where account_id ='+ str(acc_line.id) +'order by id desc limit 1')
                        row_balance = map(itemgetter(0), cr.fetchall())
                        
                        if row_debit != [] and row_debit[0] != None:
                            debit = row_debit[0]
                        if row_credit != [] and row_credit[0] != None:
                            credit = row_credit[0]
                        if row_balance != [] and row_balance[0] != None:
                            before_balance = row_balance[0]
                            
                        balance = debit - credit + before_balance
                        ineco_id = ineco_close_accont_obj.create(cr, uid, {
                                        'account_id': acc_line.id,
                                        'period_id': id,
                                        'debit': debit,
                                        'credit': credit,
                                        'balance': balance,
                                        'balance_before' : before_balance,
                            })
                        
                    cr.execute('update account_journal_period set state=%s where period_id=%s', (mode, id))
                    cr.execute('update account_period set state=%s where id=%s', (mode, id))

        return {'type': 'ir.actions.act_window_close'}
    

class account_period(osv.osv):
    _inherit = "account.period"
    _description = "Add close account in period"
    
    def _sale_amount(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('journal_id.print_sale_tax','!=',False),('period_tax_id','in',ids),('type','=','out_invoice'),('state','not in',('draft','cancel'))], context=context)
        invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_ids, context=context) 
        for invoce_sale in self.browse(cr, uid, ids, context=context):
            res[invoce_sale.id] = {'sale_amount_untaxed': 0.0,
                                   'sale_amount_tax': 0.0
                                   }
            sale_untaxed = 0.0
            sale_tax = 0.0
            for line in invoice_obj:
                sale_untaxed +=  line.amount_untaxed
                sale_tax += line.amount_tax
            res[invoce_sale.id]['sale_amount_untaxed'] = sale_untaxed
            res[invoce_sale.id]['sale_amount_tax'] = sale_tax
        return res
    
    def _sale_refund_amount(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('journal_id.print_sale_tax','!=',False),('period_tax_id','in',ids),('type','=','out_refund'),('state','not in',('draft','cancel'))], context=context)
        invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_ids, context=context) 
        for invoce_sale in self.browse(cr, uid, ids, context=context):
            res[invoce_sale.id] = {'sale_refund_amount_untaxed': 0.0,
                                   'sale_refund_amount_tax': 0.0
                                   }
            sale_untaxed = 0.0
            sale_tax = 0.0
            for line in invoice_obj:
                sale_untaxed +=  line.amount_untaxed
                sale_tax += line.amount_tax
            res[invoce_sale.id]['sale_refund_amount_untaxed'] = sale_untaxed
            res[invoce_sale.id]['sale_refund_amount_tax'] = sale_tax
        return res  
      
    def _purchase_amount(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('journal_id.print_sale_tax','!=',False),('period_tax_id','in',ids),('type','=','in_invoice'),('state','not in',('draft','cancel'))], context=context)
        invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_ids, context=context) 
        for invoce_sale in self.browse(cr, uid, ids, context=context):
            res[invoce_sale.id] = {'purchase_amount_untaxed': 0.0,
                                   'purchase_amount_tax': 0.0
                                   }
            sale_untaxed = 0.0
            sale_tax = 0.0
            for line in invoice_obj:
                sale_untaxed +=  line.amount_untaxed
                sale_tax += line.amount_tax
            res[invoce_sale.id]['purchase_amount_untaxed'] = sale_untaxed
            res[invoce_sale.id]['purchase_amount_tax'] = sale_tax
        return res

    def _purchase_refund_amount(self, cr, uid, ids, name, args, context=None):
        
        res = {}
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('journal_id.print_sale_tax','!=',False),('period_tax_id','in',ids),('type','=','in_refund'),('state','not in',('draft','cancel'))], context=context)
        invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_ids, context=context) 
        for invoce_sale in self.browse(cr, uid, ids, context=context):
            res[invoce_sale.id] = {'purchase_refund_amount_untaxed': 0.0,
                                   'purchase_refund_amount_tax': 0.0
                                   }
            sale_untaxed = 0.0
            sale_tax = 0.0
            for line in invoice_obj:
                sale_untaxed +=  line.amount_untaxed
                sale_tax += line.amount_tax
            res[invoce_sale.id]['purchase_refund_amount_untaxed'] = sale_untaxed
            res[invoce_sale.id]['purchase_refund_amount_tax'] = sale_tax
        return res
    
    def _sale_receipt_amount(self, cr, uid, ids, name, args, context=None):        
        res = {}
        invoice_ids = self.pool.get('account.voucher').search(cr, uid, [('journal_id.print_sale_tax','!=',False),('period_tax_id','in',ids),('type','=','sale'),('state','not in',('draft','cancel'))], context=context)
        invoice_obj = self.pool.get('account.voucher').browse(cr, uid, invoice_ids, context=context) 
        for invoce_sale in self.browse(cr, uid, ids, context=context):
            res[invoce_sale.id] = {'sale_receipt_amount_untaxed': 0.0,
                                   'sale_receipt_amount_tax': 0.0
                                   }
            sale_untaxed = 0.0
            sale_tax = 0.0
            for line in invoice_obj:
                sale_untaxed +=  line.amount or 0.0
                sale_tax += line.tax_amount or 0.0
            res[invoce_sale.id]['sale_receipt_amount_untaxed'] = sale_untaxed
            res[invoce_sale.id]['sale_receipt_amount_tax'] = sale_tax
        return res

    def _purchase_receipt_amount(self, cr, uid, ids, name, args, context=None):        
        res = {}
        invoice_ids = self.pool.get('account.voucher').search(cr, uid, [('journal_id.print_sale_tax','!=',False),('period_tax_id','in',ids),('type','=','purchase'),('state','not in',('draft','cancel'))], context=context)
        invoice_obj = self.pool.get('account.voucher').browse(cr, uid, invoice_ids, context=context) 
        for invoce_sale in self.browse(cr, uid, ids, context=context):
            res[invoce_sale.id] = {'purchase_receipt_amount_untaxed': 0.0,
                                   'purchase_receipt_amount_tax': 0.0
                                   }
            sale_untaxed = 0.0
            sale_tax = 0.0
            for line in invoice_obj:
                sale_untaxed +=  line.amount or 0.0
                sale_tax += line.tax_amount or 0.0
            res[invoce_sale.id]['purchase_receipt_amount_untaxed'] = sale_untaxed
            res[invoce_sale.id]['purchase_receipt_amount_tax'] = sale_tax
        return res
    
    _columns = {
        'close_line_ids': fields.one2many('ineco.close.account', 'period_id', 'Account', readonly=True),
        'customer_invoice_ids': fields.one2many('account.invoice', 'period_tax_id', 'Customer Invoice', domain=[('type','=','out_invoice'),('journal_id.print_sale_tax','!=',False)], readonly=True),        
        'customer_refund_ids': fields.one2many('account.invoice',  'period_tax_id', 'Customer Refund',  domain=[('type','=','out_refund'),('journal_id.print_sale_tax','!=',False)], readonly=True),   
        'supplier_invoice_ids': fields.one2many('account.invoice', 'period_tax_id', 'Supplier Invoice', domain=[('type','=','in_invoice'),('journal_id.print_sale_tax','!=',False)], readonly=True),   
        'supplier_refund_ids': fields.one2many('account.invoice',  'period_tax_id', 'Supplier Refund',  domain=[('type','=','in_refund'),('journal_id.print_sale_tax','!=',False)], readonly=True),
        'sale_receipt_ids': fields.one2many('account.voucher', 'period_tax_id', 'Sale Receipt', domain=[('type','=','sale'),('journal_id.print_sale_tax','!=',False)], readonly=True),        
        'purchase_receipt_ids': fields.one2many('account.voucher', 'period_tax_id', 'Purchase Receipt', domain=[('type','=','purchase'),('journal_id.print_sale_tax','!=',False)], readonly=True),        
        'sale_amount_untaxed': fields.function(_sale_amount,digits_compute=dp.get_precision('Account'), string='Amount Untaxed',multi='sums'),
        'sale_amount_tax': fields.function(_sale_amount,digits_compute=dp.get_precision('Account'), string='Amount Tax',multi='sums'),
        'sale_refund_amount_untaxed': fields.function(_sale_refund_amount,digits_compute=dp.get_precision('Account'), string='Amount Untaxed',multi='sumsr'),
        'sale_refund_amount_tax': fields.function(_sale_refund_amount,digits_compute=dp.get_precision('Account'), string='Amount Tax',multi='sumsr'),
        'purchase_amount_untaxed': fields.function(_purchase_amount,digits_compute=dp.get_precision('Account'), string='Amount Untaxed',multi='sumss'),
        'purchase_amount_tax': fields.function(_purchase_amount,digits_compute=dp.get_precision('Account'), string='Amount Tax',multi='sumss'),
        'purchase_refund_amount_untaxed': fields.function(_purchase_refund_amount,digits_compute=dp.get_precision('Account'), string='Amount Untaxed',multi='sumsp'),
        'purchase_refund_amount_tax': fields.function(_purchase_refund_amount,digits_compute=dp.get_precision('Account'), string='Amount Tax',multi='sumsp'),
        'sale_receipt_amount_untaxed': fields.function(_sale_receipt_amount,digits_compute=dp.get_precision('Account'), string='Amount Untaxed',multi='sumss1'),
        'sale_receipt_amount_tax': fields.function(_sale_receipt_amount,digits_compute=dp.get_precision('Account'), string='Amount Tax',multi='sumss1'),
        'purchase_receipt_amount_untaxed': fields.function(_purchase_receipt_amount,digits_compute=dp.get_precision('Account'), string='Amount Untaxed',multi='sumss2'),
        'purchase_receipt_amount_tax': fields.function(_purchase_receipt_amount,digits_compute=dp.get_precision('Account'), string='Amount Tax',multi='sumss2'),
        'date_pp30': fields.date('Date PP30'),
        'date_wht': fields.date('Date WHT'),
    }
    
    def action_draft(self, cr, uid, ids, *args):
        mode = 'draft'
        cr.execute('delete from ineco_close_account where period_id =%s',tuple(ids))
        cr.execute('update account_journal_period set state=%s where period_id in %s', (mode, tuple(ids),))
        cr.execute('update account_period set state=%s where id in %s', (mode, tuple(ids),))
        return True

class ineco_close_account(osv.osv):
    _name = "ineco.close.account"
    _description = "Close Account for Account Code"    
    _columns = {
        'name': fields.related('account_id', 'name',  string='Account Name', size=256,  store=True, type='char'),
        'code': fields.related('account_id', 'code',  string='Account Code', size=64,  store=True, type='char' ),
        'account_id': fields.many2one('account.account', 'Account',required=True,readonly=True),   
        'period_id': fields.many2one('account.period', 'Period',required=True,readonly=True),   
        'debit': fields.float('Debit', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'credit': fields.float('Credit', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'balance_before': fields.float('Balance Before', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'balance': fields.float('Balance', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        }
    _defaults = {
        'balance': 0.00,
        'debit': 0.00,
        'credit': 0.00,
        'balance_before': 0.00,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }
    _sql_constraints = [
        ('account_period_uniq', 'unique(account_id, period_id)', 'Account and Period Name must be unique per company!'),
    ]    
    
ineco_close_account()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: