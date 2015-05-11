# -*- coding: utf-8 -*-
# Copyright (C) 2011 Almacom (Thailand) Ltd.
# All rights reserved.

import decimal_precision as dp

from osv import osv, fields
import time
import datetime
from mx import DateTime
from tools.translate import _
import netsvc
import re
#from pprint import pprint
#from ac_utils import num2word, check_sum_pin, check_sum_tin, compute_discount, check_discount_fmt, one2many_dom

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'name': fields.char('Company Name', size=64, required=True,translate=1),
        'date_start': fields.date('Company Start',required=True),
        'department_code': fields.char('Department Code', size=4,help="Use for Thai VAT report"),

        'cq_postdate_in':fields.many2one('account.account','Post Date Cheque(Receive)'),
        'cq_postdate_out':fields.many2one('account.account','Post Date Cheque(Payment)'),

        'advance':fields.many2one('account.account','Advance Account'),
        'advance_delay':fields.integer('Advance Delay',help="Number of date that request to clear advance"),

        'cash':fields.many2one('account.account','Cash Account'),

        'inter_company_account_id':fields.many2one('account.account','Inter-Company Account'),

        'bank_charge': fields.many2one('account.account','Bank Charge Account',help="Bank Charge Account"),

        'in_invoice_journal_id':fields.many2one('account.journal','Credit Purchase',help='Journal for Credit Purchase'),
        'in_cash_journal_id':fields.many2one('account.journal','Cash Purchase',help='Journal for Cash Purchase'),
        'in_deposit_journal_id':fields.many2one('account.journal','Purchase Deposit',help='Journal Purchase Deposit'),
        'in_refund_journal_id':fields.many2one('account.journal','Credit Note',help='Journal for Purchase Credit Note'),
        'in_charge_journal_id':fields.many2one('account.journal','Debit Note',help='Journal for Purchase Debit Note'),

        'out_invoice_journal_id':fields.many2one('account.journal','Credit Sale',help='Journal for Credit Sale'),
        'out_cash_journal_id':fields.many2one('account.journal','Cash Sale',help='Journal for Cash Sale'),
        'out_deposit_journal_id':fields.many2one('account.journal','Sale Deposit',help='Journal for Sale Deposit'),
        'out_refund_journal_id':fields.many2one('account.journal','Sale Credit Note',help='Journal for Sale Credit Note'),
        'out_charge_journal_id':fields.many2one('account.journal','Sale Debit Note',help='Journal for Sale Debit Note'),

        'in_cheque_journal_id': fields.many2one('account.journal','Cheque Receipt',help="Journal for Cheque Receive"),
        'out_cheque_journal_id': fields.many2one('account.journal','Cheque Payment',help="Journal for Cheque Payment"),

        'advance_journal_id': fields.many2one('account.journal','Advance',help="Journal for Advance"),
        'bank_journal_id': fields.many2one('account.journal','Bank',help="Journal for Bank"),
        'in_petty_journal_id': fields.many2one('account.journal','Petty Cash Receipt',help="Journal for Petty cash Receipt"),
        'out_petty_journal_id': fields.many2one('account.journal','Petty Cash Payment',help="Journal for Petty cash Payment"),

        'in_payment_journal_id': fields.many2one('account.journal','Receipt',help="Journal for Receipt"),
        'out_payment_journal_id': fields.many2one('account.journal','Payment',help="Journal for Payment"),

        'wht_company_id': fields.many2one('account.account','WHT Company',help="Account for wht company"),
        'wht_personal_id': fields.many2one('account.account','WHT Personal',help="Account for wht personal"),

        'property_exchange_gain': fields.many2one('account.account',string="Exchange Rate Gain Account"),
        'property_exchange_loss': fields.many2one('account.account',string="Exchange Rate Loss Account"),

        #company info
        'addr_building': fields.char('Building', size=64),
        'addr_room_no': fields.char('Room No', size=32),
        'addr_floor': fields.char('Floor', size=32),
        'addr_village': fields.char('Village', size=64),
        'addr_no': fields.char('No', size=32),
        'addr_moo': fields.char('Moo', size=10),
        'addr_soi': fields.char('Soi', size=64),
        'addr_street': fields.char('Street', size=64),
        'addr_sub_district': fields.char('Street', size=64),
        'addr_district': fields.char('District', size=64),
        'addr_province': fields.char('Province', size=64),
        'addr_zipcode': fields.char('Zipcode', size=5),
        'addr_tel': fields.char('Tel', size=32),
    }

    _defaults={
        'date_start': lambda *a : time.strftime('%Y-01-01'),
    }

    def get_companies(self,cr,uid,context):
        company_type= context.get('company_type','parent')
        context.update({'company_type':company_type})

        res = self.pool.get('res.company').name_search(cr, uid, '', [], context=context, limit=None)
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        company_type = context.get('company_type','')
        if company_type=='child':
            args += [('parent_id','!=',False)]
        elif company_type=='parent':
            args += [('parent_id','=',False)]

        if name:
            args+=[('name', operator, name)]

        ids = self.search(cr,user,args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)

    def get_company(self,cr,uid,context=None):
        """
        @params: uid,context
        return: company browse obj
        """
        if not context:
            context={}
        #get company from user by default
        user_company_id = self.pool.get('res.users').browse(cr,uid,uid).company_id.id
        #get company from context
        company_id=context.get('company_id',False)
        if not company_id:
            company_id=user_company_id

        if context.get('main_company'):
            company_id = self.get_main_company(cr, uid, company_id, context)

        return self.browse(cr,uid,company_id)

    #TODO: improve this
    def get_main_company(self,cr,uid,company_id,context=None):
        main_company_id = False
        #search the main company
        companies = self.search(cr,uid,[('id','child_of',[company_id])])
        for company in self.browse(cr,uid,companies):
            if company.parent_id:
                main_company_id = company.parent_id.id
                break
        return main_company_id or company_id
res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
