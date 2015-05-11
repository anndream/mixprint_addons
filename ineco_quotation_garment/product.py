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
# self.browse(cr, uid, ids):
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#import math
#import re

#from _common import rounding

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

#import openerp.addons.decimal_precision as dp

class product_category(osv.osv):
    
    _inherit = 'product.category'
    _description = 'add ratio for garment'
    _columns = {
        'ratio': fields.float('Ratio', digits=(16,4)),
        'cost_type_ids': fields.one2many('ineco.category.costtype','product_category_id','Costs'),
    }
    _defaults = {
        'ratio': 1.0000
    }

class ineco_category_costtype(osv.osv):

    def on_change_costtype(self, cr, uid, ids, cost_type_id, context=None):
        if context==None:
            context={}
        result = 0.0
        cost_type_obj = self.pool.get('ineco.cost.type').browse(cr, uid, cost_type_id)
        if cost_type_obj:
            result = cost_type_obj.cost
        return {'value': {
            'cost': result,
            }
        }
    
    _name = 'ineco.category.costtype'
    _description = 'Category Description CostType'
    _columns = {
        'name': fields.char('Description',size=32,),
        'cost_type_id': fields.many2one('ineco.cost.type','Cost Type'),
        'quantity': fields.integer('Quantity'),
        'cost': fields.integer('Cost'),
        'product_category_id': fields.many2one('product.category','Product Category'),
    }
    _defaults = {
        'quantity': 1.0, 
        'cost': 1.0,
    }


class product_product(osv.osv):
    
    def _get_lot_count(self, cr, uid, ids, name, arg, context=None):
        res = {}
        lot_obj = self.pool.get('stock.production.lot')
        for id in ids:
            #lot_ids = lot_obj.search(cr, uid, [('product_id','=',id),('stock_available', '>', 0)])
            #res[id] = len(lot_ids)
            cr.execute("""
select sum(total) as total from
(select 
  count(*) as total
from stock_report_prodlots 
where product_id = %s and location_id in (select id from stock_location where usage = 'internal' and active = true) and prodlot_id is not null
group by product_id, prodlot_id, location_id
having (sum(qty) > 0.00)
) a""", (id,))
            res[id] = cr.fetchone()[0] or 0.0
        return res
    
    _inherit = 'product.product'
    _columns = {
        'lot_count': fields.function(_get_lot_count, string="Lots", type='integer',),
        'no_return_product': fields.boolean('No Return'),
        'product_name_eng': fields.char('English Name', size=128),
        'pattern': fields.boolean('Pattern'),
    }
    _defaults = {
        'no_return_product': False,
        'pattern': False,
    }

class ineco_product_category_stock(osv.osv):
    
    def _get_stock_fg(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids):
            if data.virtual_available:
                res[data.id] = round(data.qty_available * data.product_id.categ_id.ratio or 1.0000 )
            else:
                res[data.id] = 0
        return res

    def _get_stock_uom(self, cr, uid, ids, name, arg, context=None):
        res = {} 
        for id in ids:
            res[id] = u'ตัว'
        return res

    def _get_stock_rule(self, cr, uid, ids, name, arg, context=None):
        res = {} 
        orderpoint = self.pool.get('stock.warehouse.orderpoint')
        for data in self.browse(cr, uid, ids):
            res[data.id] = {
                'product_rule_count': 0,
                'product_rule_min': 0,
            }
            count_ids = orderpoint.search(cr, uid, [('product_id','=',data.product_id.id)])
            min_stock = 0
            for rule in orderpoint.browse(cr,uid, count_ids):
                min_stock += rule.product_min_qty
            res[data.id]['product_rule_count'] = len(count_ids)
            res[data.id]['product_rule_min'] = min_stock
        return res
    
    _name = 'ineco.product.category.stock'
    _auto = False

    _columns = {
        'category_id': fields.many2one('product.category','Category'),
        'category_child_id': fields.many2one('product.category','Child Category'),
        'product_id': fields.many2one('product.product','Product'),
        'virtual_available': fields.related('product_id', 'virtual_available', type='float', string='Forecast', readonly=True),
        'qty_available': fields.related('product_id', 'qty_available', type='float', string='On Hand', readonly=True),
        'uom_id': fields.related('product_id','uom_id', type='many2one', relation='product.uom', string="UOM", readonly=True ),
        'product_count': fields.function(_get_stock_fg, string="Total", type='integer',),
        'product_count_uom': fields.function(_get_stock_uom, string="Unit", type='char',),
        'product_rule_count': fields.function(_get_stock_rule, string="Unit", type='char', multi="rule"),
        'product_rule_min': fields.function(_get_stock_rule, string="Unit", type='char', multi="rule"),
    }
    
    _order = 'category_id desc, category_child_id'
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_product_category_stock')  
        cr.execute("""
            create or replace view ineco_product_category_stock as
            select 
              pp.id::integer as id, 
              pc2.id as category_id, 
              pc.id as category_child_id, 
              pp.id::integer as product_id 
            from product_category pc
            join product_category pc2 on pc2.id = pc.parent_id
            join product_template pt on pc.id = pt.categ_id
            join product_product pp on pt.id = pp.product_tmpl_id
            where 
               (pc.id in (41,42,43) or pc.parent_id in (41,42,43)) 
               and pc.parent_id <> 26
            order by
               pc2.id, pc.id, pt.name       
        """) 
        
class ineco_product_category_stock_option(osv.osv):
    
    def _get_stock_fg(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids):
            if data.virtual_available:
                res[data.id] = round(data.qty_available / 22 * 65)
            else:
                res[data.id] = 0
        return res

    def _get_stock_uom(self, cr, uid, ids, name, arg, context=None):
        res = {} 
        for id in ids:
            res[id] = u'ตัว'
        return res

    def _get_stock_rule(self, cr, uid, ids, name, arg, context=None):
        res = {} 
        orderpoint = self.pool.get('stock.warehouse.orderpoint')
        for data in self.browse(cr, uid, ids):
            res[data.id] = {
                'product_rule_count': 0,
                'product_rule_min': 0,
            }
            count_ids = orderpoint.search(cr, uid, [('product_id','=',data.product_id.id)])
            min_stock = 0
            for rule in orderpoint.browse(cr,uid, count_ids):
                min_stock += rule.product_min_qty
            res[data.id]['product_rule_count'] = len(count_ids)
            res[data.id]['product_rule_min'] = min_stock
        return res
    
    _name = 'ineco.product.category.stock.option'
    _auto = False

    _columns = {
        'category_id': fields.many2one('product.category','Category'),
        'category_child_id': fields.many2one('product.category','Child Category'),
        'product_id': fields.many2one('product.product','Product'),
        'virtual_available': fields.related('product_id', 'virtual_available', type='float', string='Forecast', readonly=True),
        'qty_available': fields.related('product_id', 'qty_available', type='float', string='On Hand', readonly=True),
        'uom_id': fields.related('product_id','uom_id', type='many2one', relation='product.uom', string="UOM", readonly=True ),
        'product_count': fields.function(_get_stock_fg, string="Total", type='integer',),
        'product_count_uom': fields.function(_get_stock_uom, string="Unit", type='char',),
        'product_rule_count': fields.function(_get_stock_rule, string="Unit", type='char', multi="rule"),
        'product_rule_min': fields.function(_get_stock_rule, string="Unit", type='char', multi="rule"),
   }
    
    _order = 'category_id desc, category_child_id'
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_product_category_stock_option')  
        cr.execute("""
            create or replace view ineco_product_category_stock_option as
            select 
              pp.id::integer as id, 
              pc2.id as category_id, 
              pc.id as category_child_id, 
              pp.id::integer as product_id 
            from product_category pc
            join product_category pc2 on pc2.id = pc.parent_id
            join product_template pt on pc.id = pt.categ_id
            join product_product pp on pt.id = pp.product_tmpl_id
            where 
               (pc.id in (96,84,108) or pc.parent_id in (96,84,108)) 
               and pc.parent_id <> 26
            order by
               pc2.id, pc.id, pt.name       
        """) 
