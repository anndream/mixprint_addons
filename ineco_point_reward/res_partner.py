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

from osv import fields, osv
#from tools.translate import _

class res_partner(osv.osv):
    
    def _point_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):            
            res[partner.id] = {
                'points': 0,
            }
            val1 = 0
            for line in partner.point_history_ids:
                if line.state == 'done':
                    val1 = val1 + (line.receive - line.issue)
            res[partner.id]['points'] = val1
        return res

    def _get_data(self, cr, uid, ids, context=None):
        result = {}
        if ids:
            ids.sort();
        for line in self.pool.get('ineco.point.history').browse(cr, uid, ids, context=context):
            result[line.partner_id.id] = True
        return result.keys()
    
    _inherit = 'res.partner'
    _columns = {
        'points': fields.function(_point_all, string='Point Total', type='integer',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'ineco.point.history': (_get_data, [], 10),
            },
            multi='sums', help="The total point."),
        #'points': fields.integer('Points'),
        'point_history_ids': fields.one2many('ineco.point.history','partner_id','Point Transaction'),        
    }
    
    def button_redemption(self, cr, uid, ids, context=None):
        return True
    
    def button_transfer(self, cr, uid, ids, context=None):
        return True

    def button_return(self, cr, uid, ids, context=None):
        return True

    def button_adjust(self, cr, uid, ids, context=None):
        return True
    