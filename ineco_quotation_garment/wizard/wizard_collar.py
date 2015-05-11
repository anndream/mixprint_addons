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
    
    _name = 'ineco.production.collar'
    _description = 'Wizard make collar'
    _columns = {
        'machine_collar_id': fields.many2one('ineco.mrp.machine', 'Collar Machine', required=True),
        'employee_collar_id': fields.many2one('hr.employee', 'Collar Employee', required=True),
    }
    
    def update_start(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            value = {
                'date_collar_start': time.strftime("%Y-%m-%d"),
                'machine_collar_id': data['machine_collar_id'][0],
                'employee_collar_id': data['employee_collar_id'][0],
            }
            self.pool.get('ineco.pattern').write(cr, uid, active_ids, value)
        return {'type': 'ir.actions.act_window_close'}

    def update_finish(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            value = {
                'date_collar_finish': time.strftime("%Y-%m-%d"),
                'machine_collar_id': data['machine_collar_id'][0],
                'employee_collar_id': data['employee_collar_id'][0],
            }
            self.pool.get('ineco.pattern').write(cr, uid, active_ids, value)            
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
