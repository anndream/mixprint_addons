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
from openerp import netsvc

class ineco_start_workorder(osv.osv_memory):
    
    _name = 'ineco.start.workorder'
    _description = 'Wizard Start Workorder'
    _columns = {
    }
    
    def update_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            wf_service = netsvc.LocalService("workflow")
            workcenter_lines = self.pool.get('mrp.production.workcenter.line').browse(cr, uid, active_ids)
            for workcenter_line in workcenter_lines:
                if workcenter_line.state == 'draft':
                    wf_service.trg_validate(uid, 'mrp.production.workcenter.line', workcenter_line.id, 'button_start_working', cr)
            
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
