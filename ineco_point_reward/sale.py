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

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import time
#import pooler
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
#from tools.translate import _
#from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import decimal_precision as dp
#import netsvc

class sale_order(osv.osv):

    def _get_point(self, cr, uid, ids, field_name, arg, context=None):

        # partner.category:
        partner_category_obj = self.pool.get('res.partner.category')
        partner_category_ids = partner_category_obj.search(cr, uid, [])
        partner_categories = partner_category_obj.read(cr, uid, partner_category_ids, ['parent_id'])
        partner_category_tree = dict([(item['id'], item['parent_id'][0]) for item in partner_categories if item['parent_id']])

        # product.category:
        product_category_obj = self.pool.get('product.category')
        product_category_ids = product_category_obj.search(cr, uid, [])
        product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

        def _create_product_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_product_category_list(parent, lst)
            else:
                return lst

        def _create_partner_category_list(id, lst):
            if not id:
                return []
            parent = partner_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_partner_category_list(parent, lst)
            else:
                return lst

        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'point_sale': 0.0,
                'point_product': 0.0,
                'point_category': 0.0,
                'point_partner': 0.0,
                'point': 0.0,
                'point_adjust': 0.0,
            }
            point_adjust = order.point_adjust
            point_sale = point_product = point_category = point_partner = 0
            if order.schema_id:
                for line in order.schema_id.line_ids:
                    if line.type == 'amount': #sale amount
                        this_point = 0
                        for value in line.value_ids:
                            if line.base_on == 'quantity':
                                if value.value <= 1:
                                    point_sale = point_sale + value.point
                            if line.base_on == 'amount':
                                if (order.amount_untaxed >= value.value) :
                                    this_point = value.point
                        point_sale = point_sale + this_point                          
                    elif line.type == 'product': #product
                        sql = """
                                select 
                                  product_id,
                                  sum(product_uom_qty) as product_qty,
                                  sum(round((product_uom_qty * price_unit) - ((product_uom_qty * price_unit) * discount / 100),2)) as amount
                                from
                                  sale_order_line sol
                                where
                                  sol.order_id = %s and state <> 'cancel'
                                group by
                                  product_id
                        """
                        cr.execute(sql % (order.id))
                        sale_lines = cr.dictfetchall()  
                        this_point_qty = this_point = 0
                        for saleline in sale_lines:
                            for value in line.value_ids:
                                if line.product_id.id == saleline['product_id']:
                                #if line.category_id.id in category_ids:
                                    if line.base_on == 'quantity':
                                        #this_point_qty = 0
                                        if saleline['product_qty'] >= value.value:
                                            this_point_qty = value.point   
                                    if line.base_on == 'amount':
                                        #this_point = 0
                                        if saleline['amount'] >= value.value:
                                            this_point = value.point   
                            point_product = point_product + this_point_qty + this_point                      
                    elif line.type == 'category': #product category
                        sql = """
                            select 
                              categ_id,
                              sum(product_uom_qty) as product_qty,
                              sum(round((product_uom_qty * price_unit) - ((product_uom_qty * price_unit) * discount / 100),2)) as amount
                            from
                              sale_order_line sol
                              join product_product pp on sol.product_id = pp.id
                              join product_template pt on pp.product_tmpl_id = pt.id
                            where
                              sol.order_id = %s and sol.state <> 'cancel'
                            group by
                              categ_id
                        """
                        cr.execute(sql % (order.id))
                        sale_lines = cr.dictfetchall()  
                        this_point_qty = this_point = 0
                        for saleline in sale_lines:
                            category_ids = _create_product_category_list(saleline['categ_id'], [saleline['categ_id']])
                            #category_ids = [saleline['categ_id']]
                            for value in line.value_ids:
                                if line.product_category_id.id in category_ids:
                                    if line.base_on == 'quantity':
                                        #this_point_qty = 0
                                        if saleline['product_qty'] >= value.value:
                                            this_point_qty = value.point   
                                    if line.base_on == 'amount':
                                        #this_point = 0
                                        if saleline['amount'] >= value.value:
                                            this_point = value.point   
                            point_category = point_category + this_point_qty + this_point                      
                    elif line.type == 'partner': #partner category
                        category_ids = [x.id for x in order.partner_id.category_id]
                        for categ_id in category_ids:
                            category_ids = _create_product_category_list(categ_id, category_ids)

                        for value in line.value_ids:
                            if line.partner_category_id.id in category_ids:
                                if line.base_on == 'quantity':
                                    if value.value <= 1:
                                        point_partner = point_partner + value.point
                                if line.base_on == 'amount':
                                    this_point = 0
                                    if order.amount_untaxed >= value.value:
                                        this_point = value.point   
                        point_partner = point_partner + this_point                      
                res[order.id] = {
                    'point_sale': point_sale,
                    'point_product': point_product,
                    'point_category': point_category,
                    'point_partner': point_partner,
                    'point': point_sale + point_product + point_category + point_partner + point_adjust,
                }
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    _inherit = "sale.order"
    _description = "Add Point Schema"
    _columns = {
        'schema_id': fields.many2one('ineco.point.schema','Point Schema'),
        'point_adjust': fields.integer('Point Adjust'),
        'point_approve': fields.boolean('Point Approved'),
        'date_point_approve': fields.datetime('Date Point Approval'),
        'point': fields.function(_get_point, digits_compute=dp.get_precision('Account'), string='Total Point',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order.line': (_get_order, [], 10),
            },
            multi='sums', 
            track_visibility='always'),
        'point_sale': fields.function(_get_point, digits_compute=dp.get_precision('Account'), string='Point Sale',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order.line': (_get_order, [], 10),
            },
            multi='sums', 
            track_visibility='always'),
        'point_product': fields.function(_get_point, digits_compute=dp.get_precision('Account'), string='Point Product',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order.line': (_get_order, [], 10),
            },
            multi='sums', 
            track_visibility='always'),
        'point_category': fields.function(_get_point, digits_compute=dp.get_precision('Account'), string='Point Category',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order.line': (_get_order, [], 10),
            },
            multi='sums', 
            track_visibility='always'),
        'point_partner': fields.function(_get_point, digits_compute=dp.get_precision('Account'), string='Point Customer',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order.line': (_get_order, [], 10),
            },
            multi='sums', 
            track_visibility='always'),
    }
    _defaults = {
        'point_adjust': 0.0,
    }

    def button_point_approve(self, cr, uid, ids, context=None):
        point_history = self.pool.get('ineco.point.history')
        for order in self.browse(cr, uid, ids, context):
            point_history_data = {
                'name': 'Receive Point',
                'docno': order.name,
                'doc_date': order.date_order,
                'sale_order_id': order.id,
                'delivery_id': False,
                'receive': order.point,
                'issue': 0,
                'balance': 0,
                'partner_id': order.partner_id.id,
            }                   
            point_history.create(cr ,uid, point_history_data)
            self.write(cr, uid, ids, {'state': 'done', 'point_approve':True, 'date_point_approve': time.strftime('%Y-%m-%d %H:%M:%S')})        
        return True

    def button_point_cancel(self, cr, uid, ids, context=None):
        point_history = self.pool.get('ineco.point.history')
        for order in self.browse(cr, uid, ids, context):
            his_id = point_history.search(cr, uid, [('sale_order_id','=',order.id),('state','=','done')])
            if his_id:
                point_history.write(cr, uid, his_id, {'state':'cancel'})
        self.write(cr, uid, ids, {'state': 'draft', 'point_approve':False, 'date_point_approve': False})        
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: