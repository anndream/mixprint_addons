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


class ineco_barcode_product_line(osv.osv):
    _name = 'ineco.barcode.product.line'
    _columns = {
        'name': fields.char('Barcode', size=64, required=True),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'date_action': fields.datetime('Date Action'),
        'product_uom': fields.many2one('product.uom','UOM'),
    }
    _defaults = {
        'product_qty': 1,
    }
 
    def on_change_barcode(self, cr, uid, id, barcode, context=None):
        if context==None:
            context={}  
        vals = {}
        product_obj = self.pool.get('product.product')
        if barcode:
            product_ids = product_obj.search(cr, uid, [('internal_barcode','=',barcode)])
            product = product_obj.browse(cr, uid, product_ids)[0]
            if product_ids:
                vals = {
                    'product_id': product.id,
                    'date_action': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'product_uom': product.uom_id.id,
                }
            else:
                raise osv.except_osv('Error!', 'Barcode Not Found!')
        return {'value':vals}
              
class stock_picking(osv.osv):
    
    _inherit = 'stock.picking'
    _columns = {
        'barcode_product_ids': fields.one2many('ineco.barcode.product.line','picking_id','Barcode by Product'),
    }
    
    def button_create_stockmove_barcode(self, cr, uid, ids, context=None):
        raise osv.except_osv('Error!',"Do This")

        for pick in self.browse(cr, uid, ids):
            model_ids = self.pool.get('ir.model.data').search(cr, uid, [('name','=','stock_location_stock')])
            default_stock_id = False
            default_stock_dest_id = False
            if model_ids:
                default_stock_id = self.pool.get('ir.model.data').browse(cr, uid, model_ids)[0].res_id
            if pick.stock_journal_id:
                default_stock_id = pick.stock_journal_id.location_id or default_stock_id
                default_stock_dest_id = pick.stock_journal_id.location_dest_id or default_stock_id
            else:
                raise osv.except_osv('Error!', 'Stock Journal Not Found!')
            for move in pick.move_lines:
                self.pool.get('stock.move').unlink(cr, uid, [move.id])
            for lot in pick.barcode_product_ids:
                if lot.product_qty <= 0:
                    raise osv.except_osv('Error!',"Please change quantity > 0")

                new_data = {
                    'picking_id': pick.id,
                    'name': lot.product_id.name or '',
                    'product_id': lot.product_id.id,
                    'product_qty': lot.product_qty,
                    'product_uos_qty': lot.product_qty,
                    'product_uom': lot.product_uom.id,
                    'product_uos': lot.product_uom.id,
                    'date': pick.date,
                    'date_expected': pick.date,
                    'location_id': default_stock_id,
                    'location_dest_id': default_stock_dest_id,
                    'partner_id': pick.partner_id.id or False,
                    #'move_dest_id': default_stock_id,
                    'state': 'draft',
                    'type':'internal',
                    'company_id': pick.company_id.id,
                    #'prodlot_id': lot.prodlot_id.id,
                }
                self.pool.get('stock.move').create(cr, uid, new_data)
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default['barcode_product_ids'] = False
        res=super(stock_picking, self).copy(cr, uid, id, default, context)
        return res
    
class stock_picking_in(osv.osv):
    
    _inherit = 'stock.picking.in'
    _columns = {
        'barcode_product_ids': fields.one2many('ineco.barcode.product.line','picking_id','Barcode by Product'),
    }
    
    def button_create_stockmove_barcode(self, cr, uid, ids, context=None):

        for pick in self.browse(cr, uid, ids):
            model_ids = self.pool.get('ir.model.data').search(cr, uid, [('name','=','stock_location_stock')])
            default_stock_id = False
            default_stock_dest_id = False
            if model_ids:
                default_stock_id = self.pool.get('ir.model.data').browse(cr, uid, model_ids)[0].res_id
            if pick.stock_journal_id:
                default_stock_id = pick.stock_journal_id.location_id or default_stock_id
                default_stock_dest_id = pick.stock_journal_id.location_dest_id or default_stock_id
            else:
                raise osv.except_osv('Error!', 'Stock Journal Not Found!')
            for move in pick.move_lines:
                self.pool.get('stock.move').unlink(cr, uid, [move.id])
            for lot in pick.barcode_product_ids:
                if lot.product_qty <= 0:
                    raise osv.except_osv('Error!',"Please change quantity > 0")

                new_data = {
                    'picking_id': pick.id,
                    'name': lot.product_id.name or '',
                    'product_id': lot.product_id.id,
                    'product_qty': lot.product_qty,
                    'product_uos_qty': lot.product_qty,
                    'product_uom': lot.product_uom.id,
                    'product_uos': lot.product_uom.id,
                    'date': pick.date,
                    'date_expected': pick.date,
                    'location_id': default_stock_id,
                    'location_dest_id': default_stock_dest_id,
                    'partner_id': pick.partner_id.id or False,
                    #'move_dest_id': lot.location_id.id,
                    'state': 'draft',
                    'type':'internal',
                    'company_id': pick.company_id.id,
                    #'prodlot_id': lot.prodlot_id.id,
                }
                self.pool.get('stock.move').create(cr, uid, new_data)
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default['barcode_product_ids'] = False
        res=super(stock_picking_in, self).copy(cr, uid, id, default, context)
        return res
    
class stock_picking_out(osv.osv):
    
    _inherit = 'stock.picking.out'
    _columns = {
        'barcode_product_ids': fields.one2many('ineco.barcode.product.line','picking_id','Barcode by Product'),
    }
    
    def button_create_stockmove_barcode(self, cr, uid, ids, context=None):

        for pick in self.browse(cr, uid, ids):
            model_ids = self.pool.get('ir.model.data').search(cr, uid, [('name','=','stock_location_stock')])
            default_stock_id = False
            default_stock_dest_id = False
            if model_ids:
                default_stock_id = self.pool.get('ir.model.data').browse(cr, uid, model_ids)[0].res_id
            if pick.stock_journal_id:
                default_stock_id = pick.stock_journal_id.location_id or default_stock_id
                default_stock_dest_id = pick.stock_journal_id.location_dest_id or default_stock_id
            else:
                raise osv.except_osv('Error!', 'Stock Journal Not Found!')
            for move in pick.move_lines:
                self.pool.get('stock.move').unlink(cr, uid, [move.id])
            for lot in pick.barcode_product_ids:
                if lot.product_qty <= 0:
                    raise osv.except_osv('Error!',"Please change quantity > 0")

                new_data = {
                    'picking_id': pick.id,
                    'name': lot.product_id.name or '',
                    'product_id': lot.product_id.id,
                    'product_qty': lot.product_qty,
                    'product_uos_qty': lot.product_qty,
                    'product_uom': lot.product_uom.id,
                    'product_uos': lot.product_uom.id,
                    'date': pick.date,
                    'date_expected': pick.date,
                    'location_id': default_stock_id,
                    'location_dest_id': default_stock_dest_id,
                    'partner_id': pick.partner_id.id or False,
                    #'move_dest_id': lot.location_id.id,
                    'state': 'draft',
                    'type':'internal',
                    'company_id': pick.company_id.id,
                    #'prodlot_id': lot.prodlot_id.id,
                }
                self.pool.get('stock.move').create(cr, uid, new_data)
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default['barcode_product_ids'] = False
        res=super(stock_picking_out, self).copy(cr, uid, id, default, context)
        return res
    