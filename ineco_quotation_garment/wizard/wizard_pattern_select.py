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

class ineco_production_selectpattern_line(osv.osv_memory):
    
    _name = 'ineco.production.selectpattern.line'
    _description = 'Line of Pattern Type'
    _columns = {
        'select_id': fields.many2one('ineco.production.selectpattern','Selected'),
        'pattern_type_id': fields.many2one('ineco.pattern.type','Pattern Type'),
        'process1': fields.boolean('Process 1 - Embroidered'),
        'process2': fields.boolean('Process 2 - Screen'),
    }

class ineco_production_selectpattern(osv.osv_memory):
    
    _name = 'ineco.production.selectpattern'
    _description = 'Wizard Select Pattern'
    _columns = {
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
        'pattern_ids': fields.one2many('ineco.production.selectpattern.line','select_id','Pattern'),
    }

    def on_change_pattern(self, cr, uid, ids, pattern_id, context=None):
        if context==None:
            context={}
        if pattern_id:
            line_obj = self.pool.get('ineco.production.selectpattern.line')
            pattern_obj = self.pool.get('ineco.pattern').browse(cr, uid, pattern_id)
            for component in pattern_obj.component_ids:
                new_data = {
                    'select_id': ids,
                    'pattern_type_id': component.type_id.id,
                    'process1': False,
                    'process2': False,
                }
                line_obj.create(cr, uid, new_data)
        return {'value': {}}    
    
    def update_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            value = {
                'pattern_id': data['pattern_id'][0],
            }
            self.pool.get('mrp.production').write(cr, uid, active_ids, value)
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
