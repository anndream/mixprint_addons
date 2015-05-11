# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 INECO Ltd., Part. (<http://www.ineco.co.th>).
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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class production_ticket_split(osv.osv_memory):
    _name = "production.ticket.split"
    _description = "Split Ticket"
    _columns = {
        'quantity': fields.float('Quantity',digits=(12,0),required=True ),
    }
    _defaults = {
        'quantity': lambda *x: 0,
    }

    def split(self, cr, uid, data, context=None):
        if context is None:
            context = {}

        rec_id = context and context.get('active_ids', False)
        move_obj = self.pool.get('ineco.mrp.production.ticket')
        quantity = self.browse(cr, uid, data[0], context=context).quantity or 0.0
        
        for move in move_obj.browse(cr, uid, rec_id, context=context):
            quantity_rest = move.quantity - quantity
            if quantity > move.quantity:
                raise osv.except_osv(_('Error!'),  _('Total quantity after split exceeds the quantity to split'))
            if quantity > 0:
                move_obj.write(cr, uid, [move.id], {
                    'quantity': quantity,
                })

            if quantity_rest>0:
                quantity_rest = move.quantity - quantity
                default_val = {
                    'quantity': quantity_rest,
                }
                current_move_id = move_obj.copy(cr, uid, move.id, default_val, context=context)

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
