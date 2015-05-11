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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
#import time
#import pooler

#from tools.translate import _
#from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import netsvc

class ineco_wht_type(osv.osv):
    _name = "ineco.wht.type"
    _description = "Type of WHT"
    _columns = {
        'name': fields.char('Description', size=256, required=True),
        'printed': fields.char('Printed', size=32),
        'seq': fields.integer('Sequence'),
    }
    _sql_constraints = [
        ('seq_unique', 'unique (seq)', 'Sequence must be unique !')
    ]
    _order = 'seq'

class ineco_wht(osv.osv):

    def _compute_tax(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for id in ids:
            result[id] = {
                'tax': 0.0,
                'base_amount': 0.0,
            }
            data = self.browse(cr, uid, [id], context=context)[0]
            val = val1 = 0.0
            for line in data.line_ids:
                val1 += line.base_amount
                val += line.tax
            result[id]['tax'] = val
            result[id]['base_amount'] = val1
        return result

    def _get_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('ineco.wht.line').browse(cr, uid, ids, context=context):
            if line:
                result[line.wht_id.id] = True
        return result.keys()
    
    _name = 'ineco.wht'
    _inherit = ['mail.thread', 'ir.needaction_mixin']    
    _description = "With holding tax"
    _columns = {
        'name': fields.char('No.', size=32, required=True),
        'date_doc': fields.date('Document Date'),
        'company_id': fields.many2one('res.company','Company', required=True),
        'partner_id': fields.many2one('res.partner','Partner', required=True),
        'account_id': fields.many2one('account.account','Account', required=True),
        'seq': fields.integer('Sequence'),
        'wht_type': fields.selection([('sale','With holding tax (Sale)'),
                                      ('purchase','With holding tax (Purchase)')],'Type of WHT'),
        'wht_kind': fields.selection([('pp1','(1) PP1'),
                                      ('pp2','(2) PP1'),
                                      ('pp3','(3) PP2'),
                                      ('pp4','(4) PP3'),
                                      ('pp5','(5) PP2'),
                                      ('pp6','(6) PP2'),
                                      ('pp7','(7) PP53'),
                                     ],'Kind of WHT'),
        'wht_payment': fields.selection([('pm1','(1) With holding tax'),
                                      ('pm2','(2) Forever'),
                                      ('pm3','(3) Once'),
                                      ('pm4','(4) Other'),
                                     ],'WHT Payment'),
        'note': fields.text('Note'),
        'line_ids': fields.one2many('ineco.wht.line', 'wht_id', 'WHT Line'),
        #'base_amount': fields.float('Base Amount', digits_compute= dp.get_precision('Account'), required=True),
        'base_amount': fields.function(_compute_tax, 
                type='float', digits_compute=dp.get_precision('Account'), string='Base Amount', 
#                store={
#                    'ineco.wht': (lambda self, cr, uid, ids, c={}: ids, [], 10),
#                    'ineco.wht.line': (_get_line, [], 10),
#                }, 
                                       multi="sums"),   
        #'tax': fields.float('Tax', digits_compute= dp.get_precision('Account'), required=True),    
        'tax': fields.function(_compute_tax, 
                type='float', digits_compute=dp.get_precision('Account'), string='Tax', 
#                store={
#                    'ineco.wht': (lambda self, cr, uid, ids, c={}: ids, [], 10),
#                    'ineco.wht.line': (_get_line, [], 10),
#                }, 
                               multi="sums"),   
                       
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ], 'Status', readonly=True,),
        'voucher_id': fields.many2one('account.voucher','Voucher'),
        }
    _defaults = {
        'wht_type': False,
        'wht_kind': 'pp4',
        'wht_payment': 'pm1',
        'name': '/',
        'date_doc': fields.date.context_today,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'ineco.wht', context=c),
        'state': 'draft',
        'wht_type': 'purchase'
    }
    _order = "date_doc, seq"

    def on_change_partner(self, cr, uid, ids, partner_id, context=None):
        value = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            value = {'wht_kind': partner.with_holding_type or False}
        return {'value': value}  
      
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}           
        default.update({
            'line_ids':False,
            'voucher_id':False,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'ineco.wht') or '/',
        })
        return super(ineco_wht, self).copy(cr, uid, id, default, context)
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            if vals.get('wht_type','purchase') == 'purchase':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'ineco.wht') or '/'
            else:
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'ineco.wht.sale') or '/'
        return super(ineco_wht, self).create(cr, uid, vals, context=context)
    
    def button_compute_tax(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for wht in self.browse(cr, uid, ids):
            tax_amount = tax = 0.0
            for line in wht.line_ids:
                tax = (((line.percent / 100) or 0.0) * line.base_amount) or 0.0
                line.write({'tax': tax})
                tax_amount += tax
            wht.write({'tax': tax_amount})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True


class ineco_wht_line(osv.osv):
    
    def _compute_tax(self, cr, uid, ids, prop, unknow_none, context=None):
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'ineco.wht')
        cur_obj = self.pool.get('res.currency')
        currency_obj = self.pool.get('res.company').browse(cr, uid, company_id).currency_id
        result = {}
        for id in ids:
            result[id] = {
                'tax': 0.0,
            }
            data = self.browse(cr, uid, [id], context=context)[0]
            total = round((((data.percent / 100) or 0.0) * data.base_amount),3) or 0.0
            total = cur_obj.round(cr, uid, currency_obj, total) 
            result[id]['tax'] = total
        return result
    
    _name = 'ineco.wht.line'
    _description = "WHT Line"
    _columns = {
        'name': fields.char('Description', size=128),
        'wht_type_id': fields.many2one('ineco.wht.type','Type',required=True),
        'date_doc': fields.date('Date', required=True),
        'percent': fields.float('Percent', digits_compute= dp.get_precision('Account'), required=True),
        'base_amount': fields.float('Base Amount', digits_compute= dp.get_precision('Account'), required=True),
        #'tax': fields.float('Tax', digits_compute= dp.get_precision('Account'), required=True),
        'tax': fields.function(_compute_tax, 
                type='float', digits_compute=dp.get_precision('Account'), string='Tax', 
#                store={'ineco.wht.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
#                      },
                                multi="sums"),   
        'wht_id': fields.many2one('ineco.wht','WHT'),
        'note': fields.char('Note', size=64),
    }
    _defaults = {
        'name': '/',
        'date_doc': fields.date.context_today,
        'percent': 3.0
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}           
        default.update({
            'wht_id':False,
        })
        return super(ineco_wht_line, self).copy(cr, uid, id, default, context)
    
class ineco_wht_pnd(osv.osv):
    _name = 'ineco.wht.pnd'
    _description = "WHT PND"
    
    def _compute_tax(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for id in ids:
            result[id] = {
                'total_amount': 0.0,
                'total_tax': 0.0,
                'total_tax_send':0.0,
            }
            data = self.browse(cr, uid, [id], context=context)[0]
            val = val1 = 0.0
            for line in data.wht_ids:
                val1 += line.base_amount
                val += line.tax
                
            result[id]['total_tax'] = val
            result[id]['total_amount'] = val1
            result[id]['total_tax_send'] = val + data.add_amount or 0.0
            
        return result
    
    def _compute_line(self, cr, uid, ids, prop, unknow_none, context=None):    
        result = {}
        for id in ids:
            result[id] = {
                'attach_count': 0,
                'attach_no': 0,
            }
            data = self.browse(cr, uid, [id], context=context)[0]
            
            count_line = len(data.wht_ids)
            count_page = count_line / 6 + 1
            result[id]['attach_count'] = count_line
            result[id]['attach_no'] = count_page
            
        return result
    
    _columns = {
        'name': fields.char('Description', size=128),
        'date_pnd': fields.date('Date', required=True), 
        'type_normal':  fields.boolean('Normal Type'),
        'type_special': fields.boolean('Special Type'),   
        'type_no': fields.integer('Type No.'),
        'section_3': fields.boolean('Section 3'),
        'section_48': fields.boolean('Section 48'),
        'section_50': fields.boolean('Section 50'),
        'section_65': fields.boolean('Section 65'),
        'section_69': fields.boolean('Section 69'),        
        'attach_pnd': fields.boolean('Attach PND'),
        'attach_count': fields.function(_compute_line,type='integer',string='Attach Count',multi="sums2"),
        'attach_no': fields.function(_compute_line,type='integer',string='Attach No',multi="sums2"),        
        'total_amount': fields.function(_compute_tax, 
                type='float', digits_compute=dp.get_precision('Account'), string='Total Amount',  multi="sums"), 
        'total_tax': fields.function(_compute_tax, 
                type='float', digits_compute=dp.get_precision('Account'), string='Total Tax',  multi="sums"), 
        'add_amount': fields.float('Add Amount', digits_compute= dp.get_precision('Account')),
        'total_tax_send': fields.function(_compute_tax, 
                type='float', digits_compute=dp.get_precision('Account'), string='Total Tax Send',  multi="sums"), 
        'wht_ids': fields.many2many('ineco.wht', 'ineco_wht_pnds', 'pnd_id', 'wht_id', 'With holding tax'),       
        'note': fields.text('Note'),
        'company_id': fields.many2one('res.company','Company', required=True),
        'pnd_type': fields.selection([('pp4','(4) PP3'),('pp7','(7) PP53')], 'PND Type', required=True, select=True),
        'period_tax_id': fields.many2one('account.period','Tax Period'),
    }
    _defaults = {
        'name': '/',
        'date_pnd': fields.date.context_today,
        'type_normal': True,
        'attach_pnd': True,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'ineco.wht.pnd', context=c),
    }    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: