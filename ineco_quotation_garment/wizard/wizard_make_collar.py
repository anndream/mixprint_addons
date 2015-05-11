# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today INECO., Part., Ltd. (<http://www.ineco.co.th>).
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

#import datetime

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class ineco_production_make_collar(osv.osv_memory):
    
    _name = 'ineco.production.make.collar'
    _description = 'Wizard make collar'
    _columns = {
        'is_print': fields.boolean('Print MO'),
    }
    
    def update_start(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            value = {
                'date_process1_start': time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.pool.get('mrp.production').write(cr, uid, active_ids, value)
            for id in active_ids:
                sql = """
                    select id from mrp_production_workcenter_line
                        where production_id in (
                            select id from mrp_production
                            where sale_order_id = (
                                select distinct sale_order_id from mrp_production
                                where id = %s)
                        ) 
                        and workcenter_id = 13
                """ % (id)
                cr.execute(sql)
                value = {
                         'date_start': time.strftime("%Y-%m-%d %H:%M:%S"),
                         #'date_finished': data['date_to'],
                         'state': 'startworking',
                }
                workorder_ids = map(lambda x: x[0], cr.fetchall())
                if workorder_ids:
                    self.pool.get('mrp.production.workcenter.line').write(cr, uid, workorder_ids, value)            
        return {'type': 'ir.actions.act_window_close'}

    def update_finish(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            value = {
                'date_process1_finish': time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.pool.get('mrp.production').write(cr, uid, active_ids, value)
            for id in active_ids:
                sql = """
                    select id from mrp_production_workcenter_line
                        where production_id in (
                            select id from mrp_production
                            where sale_order_id = (
                                select distinct sale_order_id from mrp_production
                                where id = %s)
                        ) 
                        and workcenter_id = 13
                """ % (id)
                cr.execute(sql)
                value = {
                         #'date_start': time.strftime("%Y-%m-%d %H:%M:%S"),
                         'date_finished': time.strftime("%Y-%m-%d %H:%M:%S"),
                         'state': 'done',
                }
                workorder_ids = map(lambda x: x[0], cr.fetchall())
                if workorder_ids:
                    self.pool.get('mrp.production.workcenter.line').write(cr, uid, workorder_ids, value)
            
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
