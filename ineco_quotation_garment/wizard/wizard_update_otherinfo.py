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

class ineco_production_otherinfo(osv.osv_memory):
    
    _name = 'ineco.production.otherinfo'
    _description = 'Wizard inform other information'
    _columns = {
        'bill_no': fields.char('Bill No', size=10),
        'bill_type': fields.char('Material Type', size=64),
        'worker': fields.char('Worker',size=64),
        'bill_weight': fields.float('Weight'),
    }
    
    def update_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            value = {
                'bill_no': data['bill_no'],
                'bill_type': data['bill_type'],
                'worker': data['worker'],
                'bill_weight': data['bill_weight'],
            }
            self.pool.get('mrp.production').write(cr, uid, active_ids, value)
            
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
