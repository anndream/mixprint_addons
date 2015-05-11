# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

#import time
#from lxml import etree
#import openerp.addons.decimal_precision as dp

#from openerp import netsvc
#from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.osv):

    def _get_mo(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            sql = """
                select garment_order_no as garment_order_no from sale_order where name in 
                    (select regexp_split_to_table(origin, E'\\:') as sale_no from account_invoice ai where ai.id = %s)            
            """
            cr.execute(sql % order.id)
            output = cr.fetchone()
            if output:
                res[order.id] = output[0]
        return res

    def _get_so(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            sql = """
                select id from sale_order where name in 
                    (select regexp_split_to_table(origin, E'\\:') as sale_no from account_invoice ai where ai.id = %s)            
            """
            cr.execute(sql % order.id)
            output = cr.fetchone()
            if output:
                res[order.id] = output[0]
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_saleorder(self, cr, uid, ids, context=None):
        result = {}
        obj_invoice = self.pool.get('account.invoice')
        for line in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            ids_invoice = obj_invoice.search(cr, uid, [('origin','=',line.name)])
            for invoice_id in ids_invoice:
                result[invoice_id] = True
        return result.keys()
    
    def _find_partner(self, inv):
        '''
        Find the partner for which the accounting entries will be created
        '''
        #if the chosen partner is not a company and has a parent company, use the parent for the journal entries 
        #because you want to invoice 'Agrolait, accounting department' but the journal items are for 'Agrolait'
        part = inv.partner_id
#         if part.parent_id and not part.is_company:
#             part = part.parent_id
        return part
        
    _inherit = 'account.invoice'
    _columns = {
        'name': fields.char('Description', size=64, select=True, track_visibility='onchange'),
        'garment_order_no': fields.function(_get_mo, type='char', size=32, string='Germent Order No',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'account.invoice.line': (_get_order, [], 10),
                'sale.order': (_get_saleorder, [], 10),
            },
        ),
        'garment_order_other': fields.char('Other MO',size=64, track_visibility='onchange'),
        'saleorder_id': fields.function(_get_so, type='many2one', relation="sale.order", size=32, string='Sale Order',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
        ),
        'partner_shipping_id': fields.related('saleorder_id','partner_shipping_id',string='Delivery Address', type="many2one", relation="res.partner",),
        'other_invoice_no': fields.char('Other Invoice No', size=64),
        'corrected': fields.boolean('Corrected', track_visibility='onchange'),
        'commission_ready': fields.related('saleorder_id','commission_ready',string='Commission', type="boolean",readonly=True),
        'commission_date': fields.date('Date Commission'),
        'commission_relate': fields.char('Relate Close Sale',size=16),
    }
    
    _defaults = {
        'corrected': False,
        'commission_date': False,
    }
    
    def button_open_payment(self, cr, uid, ids, context=None):
        if not ids: return []
        if context is None:
            context = {}
        invoice_ids = []
        data_pool = self.pool.get('ir.model.data')
        invoice = self.browse(cr, uid, ids)[0]
        action_model = False
        action = {}
        if invoice.type == 'out_invoice':
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account_voucher', "action_vendor_receipt")
            if action_model:
                action_pool = self.pool.get(action_model)
                action = action_pool.read(cr, uid, action_id, context=context)
                action['context'] = "{'default_partner_id':%s,'search_default_partner_id':%s,'default_journal_id':20,'default_type':'receipt'}" % (invoice.partner_id.id,invoice.partner_id.id)
                action['domain'] = "[('partner_id','=',%s)]" % (invoice.partner_id.id)
        elif invoice.type == 'in_invoice':
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account_voucher', "action_vendor_payment")
            if action_model:
                action_pool = self.pool.get(action_model)
                action = action_pool.read(cr, uid, action_id, context=context)
                action['context'] = "{'default_partner_id':%s,'search_default_partner_id':%s,'default_journal_id':35,'default_type':'payment'}" % (invoice.partner_id.id,invoice.partner_id.id)
                action['domain'] = "[('partner_id','=',%s)]" % (invoice.partner_id.id)
            
        return action

class account_voucher(osv.osv):
    
    _inherit = 'account.voucher'

    def button_get_billnumber(self, cr, uid, ids, context=None):
        obj_seq = self.pool.get('ir.sequence')
        for picking in self.browse(cr, uid, ids):
            next_number = obj_seq.next_by_code(cr, uid, 'ineco.billing', context=context)
            picking.write({'bill_number': next_number})
        return True

