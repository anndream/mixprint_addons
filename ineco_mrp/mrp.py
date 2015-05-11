# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITE (<http://www.ineco.co.th>).
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
from datetime import datetime, timedelta
from openerp import netsvc

class ineco_mrp_box(osv.osv):
    
    def _get_lastaction_date(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            sql = """
                select date_action from ineco_mrp_box_activity
                where box_id = %s
                order by date_action desc 
                limit 1
            """
            cr.execute(sql % obj.id)
            last_date = cr.fetchone()[0] or False
            if last_date:
                result[obj.id] = last_date
            else:
                result[obj.id] = False
        return result
    
    _name = "ineco.mrp.box"
    _description = "Box Master"
    _columns = {
        'name': fields.char('Box Code', size=32,required=True),
        'production_id': fields.many2one('mrp.production', 'Production',),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
        'employee_id': fields.many2one('hr.employee', 'Employee',),
        'last_action_datetime': fields.datetime('Last Action'),
        'last_ip_address': fields.char('Last IP Address', size=32),
        'last_hostname': fields.char('Last Hostname', size=32),
        'active': fields.boolean('Active'),
    }
    _sql_constraints = [
        ('name', 'unique(name)', 'The name of the Box Master must be unique')
    ]
    _defauts = {
        'active': True,
    }
    
class ineco_mrp_box_activity(osv.osv):
    _name = 'ineco.mrp.box.activity'
    _description = 'Box Activity'
    _columns = {
        'name': fields.char('Description',size=64,),
        'date_action': fields.datetime('Date Action', required=True),
        'quantity': fields.integer('Quantity', required=True),
        'box_id': fields.many2one('ineco.mrp.box','Box'),
        'workcenter_id': fields.many2one('mrp.workcenter','Workcenter',),
        'employee_id': fields.many2one('hr.employee','Employee',),
        'workorder_id': fields.many2one('mrp.production.workcenter.line','Work Order',),
    }
    
    def create(self, cr, uid, vals, context=None):
        if 'date_action' not in vals:
            vals['date_action'] = fields.datetime.context_timestamp(cr, uid, context)
        return super(ineco_mrp_box_activity, self).create(cr, uid, vals, context=context)
    
class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns = {
        'min_cycle_time': fields.integer('Minimum Cycle Time (Sec)'),
        'activity_ids': fields.one2many('ineco.mrp.box.activity','workorder_id','Activities'),
        'cycle_count': fields.float('Cycle Counts', digits=(16,2)),
    }
    _defaults = {
        'cycle_count': 0.0,
    }
    
    def action_done_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        self.pool.get('mrp.production.workcenter.line').write(cr, uid, ids, {'state': 'draft'})
        for doc_id in ids:
            cr.execute("select id from wkf where osv = '"+'mrp.production.workcenter.line'+"'")
            wkf_ids = map(lambda x: x[0], cr.fetchall())
            wkf_id = wkf_ids[0]
            cr.execute("select id from wkf_activity where wkf_id = %s and name = 'draft'" % (wkf_id))
            act_ids = map(lambda x: x[0], cr.fetchall())
            act_id = act_ids[0]
            cr.execute('update wkf_instance set state=%s where res_id=%s and res_type=%s', ('active', doc_id, 'mrp.production.workcenter.line'))
            cr.execute("update wkf_workitem set state = 'active', act_id = %s where inst_id = (select id from wkf_instance where wkf_id = %s and res_id = %s)", (str(act_id), str(wkf_id), doc_id))
        
        return True

    
class mrp_routing_workcenter(osv.osv):
    _inherit = 'mrp.routing.workcenter'
    _description = 'Minimum Cycle Time (Sec)'
    _columns = {
        'min_cycle_time': fields.integer('Minimum Cycle Time (Sec)'),
    }
    _defaults = {
        'min_cycle_time': 1,
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: