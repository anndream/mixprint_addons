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

class ineco_production_copypattern(osv.osv_memory):
    
    _name = 'ineco.production.copypattern'
    _description = 'Wizard Copy Pattern'
    _columns = {
        'pattern_id': fields.many2one('ineco.pattern','Source Pattern', required=True),
    }
    
    def update_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            pattern_id = data['pattern_id'][0]
            pattern_component_src_ids = self.pool.get('ineco.pattern.component').search(cr, uid, [('pattern_id','=',pattern_id)])
            component_obj = self.pool.get('ineco.pattern.component')
            for active_id in active_ids:
                for component in self.pool.get('ineco.pattern.component').browse(cr, uid, pattern_component_src_ids):
                    component_obj.create(cr, uid, {
                        'name': component.name,
                        'seq': component.seq,
                        'type_id': component.type_id.id,
                        'pattern_id': active_id,
                    })

        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
