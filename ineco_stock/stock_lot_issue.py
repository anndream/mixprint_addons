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

# 2014-01-24    POP-1    Bug in stock date datetime

#from lxml import etree
#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import datetime
import time
#from operator import itemgetter
#from itertools import groupby

from openerp.osv import fields, osv
#from openerp.tools.translate import _
#from openerp import netsvc
from openerp import tools
#from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class ineco_stock_lot_issue(osv.osv):
    _name = 'ineco.stock.lot.issue'
    _columns = {
        'name': fields.char('Barcode', size=128, required=True),
        'prodlot_id': fields.many2one('stock.production.lot','Serial Number', required=True),
        'product_id': fields.related('prodlot_id','product_id',type='many2one',relation='product.product',string='Product'),
        'location_id': fields.many2one('stock.location','Location',required=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True),
        'picking_id': fields.many2one('stock.picking', 'Picking', ),
        'uom_id': fields.related('product_id','uom_id',type='many2one',relation='product.uom',string='Uom'),
    }
    _defaults = {
        'name': False,
    }

    def on_barcode(self, cr, uid, ids, barcode, context=None):
        value = {}

        if barcode:
            prodlot = self.pool.get('stock.production.lot').browse(cr, uid, [barcode])[0]
            if prodlot:
                list_ids = self.pool.get('ineco.stock.list').search(cr, uid, [('prodlot_id.id','=',prodlot.id),('on_hand','>',0),('is_stock','=','STOCK')])
                if list_ids:
                    list_stock_obj = self.pool.get('ineco.stock.list').browse(cr, uid, list_ids)[0]
                    value = {
                             'prodlot_id':prodlot.id,
                             'product_id':list_stock_obj.product_id.id,
                             'location_id': list_stock_obj.location_dest_id.id, 
                             'product_qty':list_stock_obj.on_hand,
                             'uom_id':list_stock_obj.product_id.uom_id.id}
                else:
                    value = {'prodlot_id':False,'product_id':False, 'location_id': False, 'product_qty':False,'uom_id':False}
                    raise osv.except_osv('Error!', 'Serial Number Not Found in Stock List!')

        return {'value': value}
     
    def on_prodlot_id(self, cr, uid, ids, prodlot_id, context=None):
        value = {}

        if prodlot_id:
            list_ids = self.pool.get('ineco.stock.list').search(cr, uid, [('prodlot_id','=',prodlot_id),('on_hand','>',0),('is_stock','=','STOCK')])
            if list_ids:
                list_stock_obj = self.pool.get('ineco.stock.list').browse(cr, uid, list_ids)[0]
                value = {'product_id':list_stock_obj.product_id.id,
                         'location_id': list_stock_obj.location_dest_id.id, 
                         'product_qty':list_stock_obj.on_hand,
                         'uom_id':list_stock_obj.product_id.uom_id.id,
                         'name': prodlot_id}
            else:
                value = {'prodlot_id':False,'product_id':False, 'location_id': False, 'product_qty':False,'uom_id':False}
                raise osv.except_osv('Error!', 'Serial Number Not Found!')

        return {'value': value}
    

class stock_picking(osv.osv):
    
    _inherit = 'stock.picking'
    _columns = {
        'prodlot_ids': fields.one2many('ineco.stock.lot.issue','picking_id','Production Lots'),
        'production_id': fields.many2one('mrp.production','Manufacturing Order'),
        'production_ids': fields.many2many('mrp.production', 'picking_production_rel', 'picking_id', 'production_id', 'Productions'),
    }
        
    def button_create_stockmove(self, cr, uid, ids, context=None):
        for pick in self.browse(cr, uid, ids):
            for move in pick.move_lines:
                self.pool.get('stock.move').unlink(cr, uid, [move.id])
            for lot in pick.prodlot_ids:
                if lot.product_qty <= 0:
                    raise osv.except_osv('Error!',"Please change quantity > 0")

                new_data = {
                    'picking_id': pick.id,
                    'name': lot.product_id.name or '',
                    'product_id': lot.product_id.id,
                    'product_qty': lot.product_qty,
                    'product_uos_qty': lot.product_qty,
                    'product_uom': lot.uom_id.id,
                    'product_uos': lot.uom_id.id,
                    'date': pick.date,
                    'date_expected': pick.date,
                    'location_id': lot.location_id.id,
                    'location_dest_id': lot.location_id.id,
                    'partner_id': pick.partner_id.id or False,
                    #'move_dest_id': lot.location_id.id,
                    'state': 'draft',
                    'type':'internal',
                    'company_id': pick.company_id.id,
                    'prodlot_id': lot.prodlot_id.id,
                }
                self.pool.get('stock.move').create(cr, uid, new_data)
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default['prodlot_ids'] = False
        res=super(stock_picking, self).copy(cr, uid, id, default, context)
        return res

class stock_picking_out(osv.osv):
    
    _inherit = 'stock.picking.out'
    _columns = {
        'prodlot_ids': fields.one2many('ineco.stock.lot.issue','picking_id','Production Lots'),
        'production_id': fields.many2one('mrp.production','Manufacturing Order'),
        'production_ids': fields.many2many('mrp.production', 'picking_production_rel', 'picking_id', 'production_id', 'Productions'),
    }
        
    def button_create_stockmove(self, cr, uid, ids, context=None):
        for pick in self.browse(cr, uid, ids):
            for move in pick.move_lines:
                self.pool.get('stock.move').unlink(cr, uid, [move.id])
            for lot in pick.prodlot_ids:
                if lot.product_qty <= 0:
                    raise osv.except_osv('Error!',"Please change quantity > 0")

                new_data = {
                    'picking_id': pick.id,
                    'name': lot.product_id.name or '',
                    'product_id': lot.product_id.id,
                    'product_qty': lot.product_qty,
                    'product_uos_qty': lot.product_qty,
                    'product_uom': lot.uom_id.id,
                    'product_uos': lot.uom_id.id,
                    'date': pick.date,
                    'date_expected': pick.date,
                    'location_id': lot.location_id.id,
                    'location_dest_id': lot.location_id.id,
                    'partner_id': pick.partner_id.id or False,
                    #'move_dest_id': lot.location_id.id,
                    'state': 'draft',
                    'type':'internal',
                    'company_id': pick.company_id.id,
                    'prodlot_id': lot.prodlot_id.id,
                }
                self.pool.get('stock.move').create(cr, uid, new_data)
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default['prodlot_ids'] = False
        res=super(stock_picking_out, self).copy(cr, uid, id, default, context)
        return res
    