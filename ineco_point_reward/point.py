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

# 28-01-2013    POP-001    Add Redemption

import time
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
#from operator import itemgetter

from openerp import netsvc

#import logging
#import pooler
from openerp.osv import fields, osv
#import decimal_precision as dp
#from tools.translate import _
#from tools.float_utils import float_round
#from openerp import SUPERUSER_ID
#import tools

class ineco_point_schema(osv.osv):
    _name = "ineco.point.schema"
    _description = "Point Reward"
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Name', size=250, required=True),
        'date_start': fields.date('Start Date'),
        'date_end': fields.date('End Date'),
        'line_ids': fields.one2many('ineco.point.schema.line','schema_id','Schemas'),
        'active': fields.boolean('Active')
    }
    _defaults = {
        'active': True,
    }
    
class ineco_point_schema_line(osv.osv):    
    _name = "ineco.point.schema.line"
    _description = "Point Schema Line"
    _columns = {
        'name': fields.char('Description', size=254, required=True),
        'seq': fields.integer('Sequence',),
        'schema_id': fields.many2one('ineco.point.schema', 'Schema', required=True),
        'type': fields.selection([('amount','Sales'),('product','Product'),('category','Product Category'),('partner','Customer Category')], 'Schema Type', required=True),
        'base_on': fields.selection([('quantity','Quantity'),('amount','Amount')], 'Base On', required=True),
        'multiple': fields.float('Multiple'),
        'partner_category_id': fields.many2one('res.partner.category', 'Customer Category'),
        'product_id': fields.many2one('product.product','Product'),
        'product_category_id': fields.many2one('product.category','Product Category'),
        'value_ids': fields.one2many('ineco.point.schema.value','schema_line_id','Schema Line'),
    }
    _defaults = {
        'name': "...",
        'type': "amount",
        'base_on': False,
        'multiple': 1,
        'seq': 1,
    }
    _sql_constraints = [
        ('schema_line_duplicate', 'unique (schema_id, type, base_on, partner_category_id, product_id, product_category_id )', 'Data must be unique (Type, BaseOn, Customer, Product, Category)!')
    ]
    
class ineco_point_schema_value(osv.osv):
    _name = "ineco.point.schema.value"
    _description = "Point Schema Value"
    _columns = {
        'name': fields.char('Description', size=100, required=True),
        'schema_line_id': fields.many2one('ineco.point.schema.line','Schema Line'),
        'value': fields.integer('Value', required=True),
        'point': fields.integer('Point', required=True),
    }
    _defaults = {
        'name': '...',
        'value': 1,
        'point': 1,
    }
    _order = 'value'
    _sql_constraints = [
        ('schema_line_value_point_unique', 'unique (schema_line_id, value, point)', 'Data must be unique (Value, Point) !')
    ]
    
class ineco_point_history(osv.osv):   

    def _get_point(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for history in self.browse(cr, uid, ids, context=context):
            res[history.id] = {
                'before_qty': 0,
                'balance': 0,
            }
            val1 = 0
            if history.partner_id:
                history_ids = self.pool.get('ineco.point.history').search(cr, uid, 
                    [('partner_id','=',history.partner_id.id),('id','<',history.id),('state','=','done') ])
                for his in self.browse(cr, uid, history_ids):
                    val1 = val1 + his.receive - his.issue
                
            res[history.id]['before_qty'] = val1
            if history.state == 'done':                
                res[history.id]['balance'] = val1 + history.receive - history.issue
        return res
     
    _name = "ineco.point.history"
    _columns = {
        'name': fields.char('Description', size=254, required=True),
        'docno': fields.char('Document Refer', size=254, required=True),
        'doc_date': fields.date('Document Date'),
        'sale_order_id': fields.many2one('sale.order','Sale Order',),
        'delivery_id': fields.many2one('stock.picking.out','Delivery Order',),
        'receive': fields.integer('Receive',),
        'issue': fields.integer('Issue',),
        #'balance': fields.integer('Balance',),
        'partner_id': fields.many2one('res.partner','Partner',required=True),
        'state': fields.selection(
            [('done', 'Done'),
            ('cancel', 'Cancel'),],
            'Status', readonly=True, select=True),  
        'before_qty': fields.function(_get_point, string='Before', type='integer',
            store={
                'ineco.point.history': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
            multi='sums', help="The point before."),
        'balance': fields.function(_get_point, string='Balance', type='integer',
            store={
                'ineco.point.history': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
            multi='sums', help="The point balance."),
    }
    
    _defaults = {
        'docno': '...',
        'name': '...',
        'receive': 0,
        'issue': 0,
        'balance': 0,
        'state':'done',
    }

#POP-001
class ineco_redemption_order(osv.osv):

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'point_total': 0,
            }
            val1 = 0
            for line in order.line_ids:
                val1 += line.product_point_total
            res[order.id]['point_total'] = val1
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('ineco.redemption.line').browse(cr, uid, ids, context=context):
            result[line.redemption_id.id] = True
        return result.keys()
    
    _name = 'ineco.redemption.order'
    _description = 'Redemption Order'
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Redemption No', size=32, required=True, select=True),
        'date_order': fields.date('Redemption Date', required=True),
        'date_done': fields.datetime('Date Done'),
        'date_confirm': fields.datetime('Date Confirm'),
        'partner_id': fields.many2one('res.partner','Customer', required=True),
        'origin': fields.char('Order Reference', size=64),        
        'note': fields.text('Note'),
        'line_ids': fields.one2many('ineco.redemption.line','redemption_id','Redemption Lines'),
        'point_total': fields.function(_amount_all, string='Point Total',
            store={
                'ineco.redemption.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'ineco.redemption.line': (_get_order, [], 10),
            },
            multi='sums', help="The total point."),
        'picking_id': fields.many2one('stock.picking.out','Picking Order'),
        'type': fields.selection(
            [('issue','Issue'),
             ('receive','Receive')],
            'Type', required=True, select=True),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('confirmed', 'Waiting Delivered'),
            ('done', 'Delivered'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True),  
        'point_balance': fields.related('partner_id','points',string='Point Balance',type='integer'),      
    }
    _defaults = {
        'state': 'draft',
    }

    def action_done(self, cr, uid, ids, context=None):
        for id in ids:
            order = self.pool.get('ineco.redemption.order').browse(cr, uid, [id])[0]
            if order.type == 'issue':
                point_history_data = {
                    'name': 'Redemption - Issue',
                    'docno': order.name,
                    'doc_date': order.picking_id.date,
                    'sale_order_id': False,
                    'delivery_id': order.picking_id.id,
                    'receive': 0,
                    'issue': order.point_total,
                    'balance': 0,
                    'partner_id': order.partner_id.id,
                }
            else:
                point_history_data = {
                    'name': 'Redemption - Receive',
                    'docno': order.name,
                    'doc_date': order.picking_id.date,
                    'sale_order_id': False,
                    'delivery_id': order.picking_id.id,
                    'receive': order.point_total,
                    'issue': 0,
                    'balance': 0,
                    'partner_id': order.partner_id.id,
                }
                
            self.pool.get('ineco.point.history').create(cr ,uid, point_history_data)
            self.write(cr, uid, ids, {'state': 'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        for id in ids:
            order = self.pool.get('ineco.redemption.order').browse(cr, uid, [id])[0]
            picking_ids = self._create_pickings(cr, uid, order, order.line_ids, False, context)
            self.write(cr, uid, ids, {'state': 'confirmed', 'date_done': False, 'date_confirm': time.strftime('%Y-%m-%d %H:%M:%S'), 'picking_id': picking_ids[0]})
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel', 'date_done': False, 'date_confirm': False, 'picking_id': False})
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        for id in ids:
            #cancel D/O
            order = self.pool.get('ineco.redemption.order').browse(cr, uid, [id])[0]
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', order.picking_id.id, 'button_cancel', cr)
            #cancel history
            history_ids = self.pool.get('ineco.point.history').search(cr, uid, [('docno','=',order.name),('state','=','done')])
            self.pool.get('ineco.point.history').write(cr, uid, history_ids, {'state':'cancel'})
            self.write(cr, uid, ids, {'state': 'draft', 'date_done': False, 'date_confirm': False, 'picking_id': False})
        return True

    def _prepare_order_picking(self, cr, uid, order, context=None):
        if order.type == 'issue':      
            return {
                'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out'),
                'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
                'date': order.date_order,
                'partner_id': order.partner_id.id,
                'invoice_state': 'none',
                'type': 'out',
                'partner_id': order.partner_id.id,
                'move_lines' : [],
            }
        else:
            return {
                'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
                'date': order.date_order,
                'partner_id': order.partner_id.id,
                'invoice_state': 'none',
                'type': 'in',
                'partner_id': order.partner_id.id,
                'move_lines' : [],
            }

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        stock_id = self.pool.get('stock.location').search(cr, uid, [('name','=','Stock')])
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'date_expected': time.strftime('%Y-%m-%d %H:%M:%S'),
            'location_dest_id': order.partner_id.property_stock_customer.id,
            'location_id': stock_id[0],
            'picking_id': picking_id,
            'partner_id': order.partner_id.id,
            'state': 'draft',
            'type':'out',
            'price_unit': order_line.product_point
        }

    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
        if not picking_id:
            picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
        todo_moves = []
        stock_move = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        for order_line in order_lines:
            if not order_line.product_id:
                continue
            if order_line.product_id.type in ('product', 'consu'):
                move = stock_move.create(cr, uid, self._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context))
                todo_moves.append(move)
        stock_move.action_confirm(cr, uid, todo_moves)
        stock_move.force_assign(cr, uid, todo_moves)
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return [picking_id]
   
#POP-001 
class ineco_redemption_line(osv.osv):
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        val1 = 0
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'product_point_total': 0,
            }
            val1 = val1 + (order.product_point * order.product_qty)
            res[order.id]['product_point_total'] = val1
        return res

    _name = 'ineco.redemption.line'
    _description = 'Redemption Line'
    _columns = {
        'name': fields.char('Description', size=128),
        'product_id': fields.many2one('product.product','Product',required=True),
        'product_uom': fields.many2one('product.uom','UOM',required=True),
        'product_qty': fields.integer('Quantity', required=True),
        'product_point': fields.integer('Point', reqruied=True),
        'product_point_total': fields.function(_amount_all, string='Total Point',
            store={
                'ineco.redemption.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
            multi='sums', help="The total point."),
        'redemption_id': fields.many2one('ineco.redemption.order','Redemption', required=True),
    }
    _defaults = {
        'product_qty': 1,
    }
    
    def product_id_change(self, cr, uid, ids, product, qty=0, uom=False, context=None):
        context = context or {}
        product_obj = self.pool.get('product.product')
        result = {}
        product_obj = product_obj.browse(cr, uid, product, context)

        result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context)[0][1]
        result['product_uom'] = product_obj.uom_id.id
        result['product_point'] = product_obj.point

        return {'value': result}
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: