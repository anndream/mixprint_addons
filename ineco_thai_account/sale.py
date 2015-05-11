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
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
#import pooler

#from tools.translate import _
#import decimal_precision as dp
#import netsvc

#class sale_shop(osv.osv):
#    _inherit = "sale.shop"
#    _description = "Add Auto Sequence"
#    _columns = {
#        'sequence_id': fields.many2one('ir.sequence', 'Sequence')
#    }

class sale_order(osv.osv):
    
    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
                    lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
            #Add Billing Due Date
            if order.partner_invoice_id.billing_payment_id:
                bill_data = inv_obj.onchange_payment_term_date_due(cr, uid, [inv_id], order.partner_invoice_id.billing_payment_id.id, data['value']['date_due'])
                inv_obj.write(cr, uid, [inv_id], bill_data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id
    
    _inherit = "sale.order"
    _description = "Add Delivery Date"
    _columns = {
        'delivery_date': fields.date('Delivery Date',),
        'ineco_delivery_type_id': fields.many2one('ineco.delivery.type', 'Delivery Type'),
        'ineco_sale_admin_id': fields.many2one('res.users','Sale Admin.'),
        'check_advnace':fields.boolean('Check Advnace'),
    }
    _defaults = {
        'ineco_sale_admin_id': lambda obj, cr, uid, context: uid,
        'check_advnace': False,
    }  

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            if vals.get('shop_id'):
                shop_obj = self.pool.get('sale.shop').browse(cr, uid, vals['shop_id'])
                if shop_obj and shop_obj.sequence_id:
                    vals['name'] = shop_obj.sequence_id.get_id()  or '/'
            else:
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
        return super(sale_order, self).create(cr, uid, vals, context=context)
    
class sale_order_line(osv.osv):
    
    _inherit = "sale.order.line"
    _description = "Add Analytic Account"
    _columns = {
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),        
    }
    
    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('account.invoice.line')
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context=context)
        i = 0
        for line in self.browse(cr, uid, ids, context=context):
            line_obj.write(cr, uid, [create_ids[i]], {'account_analytic_id': line.account_analytic_id.id})
            i = i + 1
        return create_ids
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
