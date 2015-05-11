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



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import time
from openerp.osv import fields, osv
#import openerp.decimal_precision as dp
from openerp.tools.translate import _


class account_account(osv.osv):

    _inherit = "account.account"
    _columns = {
                'account_wht':fields.boolean('With Holding Tax'),
                'report_type': fields.selection([('owner','Balance Sheet (owner account)'),
                                                ('income', 'Profit & Loss (Income account)'),
                                                ('expense', 'Profit & Loss (Expense account)'),
                                                ('asset', 'Balance Sheet (Asset account)'),
                                                ('liability','Balance Sheet (Liability account)')], 'P&L / BS Category', ),
                'cashflow_report': fields.boolean('Cash Flow Report'),         
                                        
                }      
    _defaults = {
        'report_type': 'owner',
    }
    
class account_payment_term(osv.osv):
    
    _inherit = 'account.payment.term'

    def _compute_month(self, current_date=datetime.now()):
        year, month = current_date.timetuple()[:2]
        first_day_of_month = datetime(year, month, 1)        
        if month == 12:
            first_day_of_next_month = datetime(year+1, 1, 1)
        else:
            first_day_of_next_month = datetime(year, month+1, 1)
        last_day_of_month = first_day_of_next_month - timedelta(1)
        #print first_day_of_month, last_day_of_month
        first_week_day = first_day_of_month.weekday()+1
        date_range = [0]*first_week_day + range(first_day_of_month.day,
        last_day_of_month.day+1)
        month = []
        while date_range:
            if len(date_range) >= 7:
                week = date_range[:7]
                date_range = date_range[7:]
            else:
                week = date_range
                date_range = None
            month.append(week)        
        return month
    
    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        result = []
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            if line.value == 'fixed':
                amt = round(line.value_amount, prec)
            elif line.value == 'procent':
                amt = round(value * line.value_amount, prec)
            elif line.value == 'balance':
                amt = round(amount, prec)
            if amt:
                next_date = (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=line.days))
                if line.days2 < 0:
                    next_first_date = next_date + relativedelta(day=1,months=1) #Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days2)
                if line.days2 > 0:
                    next_date += relativedelta(day=line.days2, months=1)
                #Check Week number and Day of week
                if line.weekno and line.dayofweek:
                    months = self._compute_month(next_date)
                    if int(line.weekno) == 5:
                        day = months[len(months)-1][line.dayofweek]
                    else:
                        if max(months[int(line.weekno)-1]) == 0:
                            day = months[int(line.weekno)][line.dayofweek]
                        else:
                            day = months[int(line.weekno)-1][line.dayofweek]
                    next_date = datetime(next_date.year, next_date.month, day)
                result.append( (next_date.strftime('%Y-%m-%d'), amt) )
                amount -= amt

        amount = reduce(lambda x,y: x+y[1], result, 0.0)
        dist = round(value-amount, prec)
        if dist:
            result.append( (time.strftime('%Y-%m-%d'), dist) )
        return result    
        
class account_payment_term_line(osv.osv):
    _inherit = 'account.payment.term.line'
    _columns = {
        'weekno': fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','Last')], 'Week No'),
        'dayofweek': fields.selection([(1,'Monday'),(2,'Tuesday'),(3,'Wednesday'),(4,'Thursday'),(5,'Friday'),(6,'Saturday')], 
                                      'Day of week'),
    }

class account_voucher(osv.osv):
    
    _inherit = "account.voucher"
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, \
                                                               amount, currency_id, ttype, date, context=None)
        if partner_id and date:
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner_obj.cheque_payment_id:
                date_due = self.pool.get('account.payment.term').compute(cr, uid, partner_obj.cheque_payment_id.id,\
                                                                                         1, date, context )
                res['value']['date_due'] = date_due[-1][0]
                          
        return res    

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        res = {'value':{}}
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = False
        if journal.customer :
            account_id = journal.default_debit_account_id.id
        else:
            account_id = journal.default_credit_account_id.id
        res['value']['account_id'] = account_id
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: