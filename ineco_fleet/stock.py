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

from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby
from openerp.osv.orm import except_orm

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class stock_warehouse(osv.osv):
    _inherit = 'stock.warehouse'
    _columns = {
        'code': fields.char('Code', size=16),
    }

class stock_picking(osv.osv):
    
    def _get_odometer_start(self, cr, uid, ids, odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            if record.odometer_start_id:
                res[record.id] = record.odometer_start_id.value
        return res

    def _set_odometer_start(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            return True
        date = self.browse(cr, uid, id, context=context).date_vehicle_start
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        driver_id = self.browse(cr, uid, id, context=context).driver_id
        vehicle_id = self.browse(cr, uid, id, context=context).vehicle_id
        partner_id = self.browse(cr, uid, id, context=context).partner_id
        odometer_start_id = self.browse(cr, uid, id, context=context).odometer_start_id
        if odometer_start_id:
            self.pool.get('fleet.vehicle.odometer').unlink(cr, uid, [odometer_start_id.id], context)
        data = {
            'value': value, 
            'date': date, 
            'date_start': date ,
            'vehicle_id': vehicle_id.id,
            'picking_id':id,
            'partner_id': partner_id and partner_id.id or False,
            'driver_id': driver_id and driver_id.id or False,
        }
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
        return self.write(cr, uid, id, {'odometer_start_id': odometer_id}, context=context)

    def _get_odometer_stop(self, cr, uid, ids, odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            if record.odometer_stop_id:
                res[record.id] = record.odometer_stop_id.value
        return res

    def _set_odometer_stop(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            return True
        date = self.browse(cr, uid, id, context=context).date_vehicle_stop
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).vehicle_id
        partner_id = self.browse(cr, uid, id, context=context).partner_id
        driver_id = self.browse(cr, uid, id, context=context).driver_id
        odometer_stop_id = self.browse(cr, uid, id, context=context).odometer_stop_id
        if odometer_stop_id:
            self.pool.get('fleet.vehicle.odometer').unlink(cr, uid, [odometer_stop_id.id], context)
        data = {
            'value': value, 
            'date': date, 
            'date_start': date ,
            'vehicle_id': vehicle_id.id,
            'picking_id':id,
            'partner_id': partner_id and partner_id.id or False,
            'driver_id': driver_id and driver_id.id or False,
        }
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
        return self.write(cr, uid, id, {'odometer_stop_id': odometer_id}, context=context)
    
    _inherit = "stock.picking"
    _columns = {
        'driver_id': fields.many2one('ineco.fleet.driver','Driver'),
        'vehicle_id': fields.many2one('fleet.vehicle','Vehicle'),
        'date_vehicle_start': fields.datetime('Date Start'),
        'date_vehicle_stop': fields.datetime('Date Stop'),
        'odometer_start': fields.float('Odometer Start'),
        'odometer_stop': fields.float('Odometer Stop'),
        'odometer_start_id': fields.many2one('fleet.vehicle.odometer', 'Odometer Start'),
        'odometer_start': fields.function(_get_odometer_start, fnct_inv=_set_odometer_start, type='float', string='Odometer Start Value'),  
        'odometer_stop_id': fields.many2one('fleet.vehicle.odometer', 'Odometer Stop'),
        'odometer_stop': fields.function(_get_odometer_stop, fnct_inv=_set_odometer_stop, type='float', string='Odometer Stop Value'),  
        'route_id': fields.many2one('ineco.fleet.route', 'Route'),
    }    

    def create(self, cr, user, vals, context=None):
        if (('route_id' not in vals) or (not vals['route_id'])) and ('partner_id' in vals) and ('type' in vals) and (vals['type'] == 'out'):
            partner = self.pool.get('res.partner').browse(cr, user, vals['partner_id'])
            vals['route_id'] = partner and partner.route_id and partner.route_id.id or False
        new_id = super(stock_picking, self).create(cr, user, vals, context)
        return new_id        

class stock_picking_out(osv.osv):
 
    def _get_odometer_start(self, cr, uid, ids, odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            if record.odometer_start_id:
                res[record.id] = record.odometer_start_id.value
        return res

    def _set_odometer_start(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            return True
        date = self.browse(cr, uid, id, context=context).date_vehicle_start
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        driver_id = self.browse(cr, uid, id, context=context).driver_id
        vehicle_id = self.browse(cr, uid, id, context=context).vehicle_id
        partner_id = self.browse(cr, uid, id, context=context).partner_id
        odometer_start_id = self.browse(cr, uid, id, context=context).odometer_start_id
        if odometer_start_id:
            self.pool.get('fleet.vehicle.odometer').unlink(cr, uid, [odometer_start_id.id], context)
        data = {
            'value': value, 
            'date': date, 
            'date_start': date ,
            'vehicle_id': vehicle_id.id,
            'picking_id':id,
            'partner_id': partner_id and partner_id.id or False,
            'driver_id': driver_id and driver_id.id or False,
        }
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
        return self.write(cr, uid, id, {'odometer_start_id': odometer_id}, context=context)

    def _get_odometer_stop(self, cr, uid, ids, odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            if record.odometer_stop_id:
                res[record.id] = record.odometer_stop_id.value
        return res

    def _set_odometer_stop(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            return True
        date = self.browse(cr, uid, id, context=context).date_vehicle_stop
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).vehicle_id
        partner_id = self.browse(cr, uid, id, context=context).partner_id
        driver_id = self.browse(cr, uid, id, context=context).driver_id
        odometer_stop_id = self.browse(cr, uid, id, context=context).odometer_stop_id
        if odometer_stop_id:
            self.pool.get('fleet.vehicle.odometer').unlink(cr, uid, [odometer_stop_id.id], context)
        data = {
            'value': value, 
            'date': date, 
            'date_start': date ,
            'vehicle_id': vehicle_id.id,
            'picking_id':id,
            'partner_id': partner_id and partner_id.id or False,
            'driver_id': driver_id and driver_id.id or False,
        }
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
        return self.write(cr, uid, id, {'odometer_stop_id': odometer_id}, context=context)
    
    _inherit = 'stock.picking.out'
    _columns = {
        'driver_id': fields.many2one('ineco.fleet.driver','Driver'),
        'vehicle_id': fields.many2one('fleet.vehicle','Vehicle'),
        'date_vehicle_start': fields.datetime('Date Start'),
        'date_vehicle_stop': fields.datetime('Date Stop'),
        'odometer_start': fields.float('Odometer Start'),
        'odometer_stop': fields.float('Odometer Stop'),
        'odometer_start_id': fields.many2one('fleet.vehicle.odometer', 'Odometer Start'),
        'odometer_start': fields.function(_get_odometer_start, fnct_inv=_set_odometer_start, type='float', string='Odometer Start Value'),  
        'odometer_stop_id': fields.many2one('fleet.vehicle.odometer', 'Odometer Stop'),
        'odometer_stop': fields.function(_get_odometer_stop, fnct_inv=_set_odometer_stop, type='float', string='Odometer Stop Value'),  
        'route_id': fields.many2one('ineco.fleet.route', 'Route'),
    }

    def onchange_partner_in(self, cr, uid, ids, partner_id=None, context=None):
        if context is None:
            context = {}
        output = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, [partner_id])[0]
            route_id = partner and partner.route_id and partner.route_id.id or False
            output = {'route_id': route_id}
        return {'value': output}
        
    def create(self, cr, user, vals, context=None):
        if (('route_id' not in vals) or (not vals['route_id'])) and ('partner_id' in vals) :
            partner = self.pool.get('res.partner').browse(cr, user, vals['partner_id'])
            vals['route_id'] = partner and partner.route_id and partner.route_id.id or False
        new_id = super(stock_picking_out, self).create(cr, user, vals, context)
        return new_id 