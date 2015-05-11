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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class ineco_production_updateplan(osv.osv_memory):
    
    _name = 'ineco.production.updateplan'
    _description = 'Wizard Update Start/Finish Production Plan'
    _columns = {
        'date_from': fields.datetime('From', required=True),
        'date_to': fields.datetime('To', required=True),
    }
    
    def update_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            value = {
                'date_plan_start': data['date_from'],
                'date_plan_finish': data['date_to'],
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
                        and workcenter_id = (
                            select workcenter_id from mrp_routing_workcenter 
                            where routing_id = (select routing_id from mrp_production
                                where id = %s)
                            order by sequence limit 1)
                """ % (id, id)
                cr.execute(sql)
                value = {
                         'date_start': data['date_from'],
                         'date_finished': data['date_to'],
                         'state': 'done',
                }
                workorder_ids = map(lambda x: x[0], cr.fetchall())
                if workorder_ids:
                    self.pool.get('mrp.production.workcenter.line').write(cr, uid, workorder_ids, value)
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
