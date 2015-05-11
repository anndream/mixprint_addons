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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

class purchase_order(osv.osv):

    def _prepare_order_picking(self, cr, uid, order, context=None):
        data = {}
        if order.warehouse_id and order.warehouse_id.incoming_journal_id and order.warehouse_id.incoming_journal_id.sequence_id:
            data['name'] = self.pool.get('ir.sequence').get_id(cr, uid, sequence_code_or_id = order.warehouse_id.incoming_journal_id.sequence_id.id )
            data['stock_journal_id'] = order.warehouse_id.incoming_journal_id.id 
        else:
            data['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
        data.update({
            #'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': order.date_order,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'type': 'in',
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'purchase_id': order.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
        })
        return data
        
    _inherit = 'purchase.order'

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            if vals.get('warehouse_id',False):
                warehouse_obj = self.pool.get('stock.warehouse').browse(cr, uid, vals.get('warehouse_id',False))
                if warehouse_obj and warehouse_obj.purchase_sequence_id:
                    
                    vals['name'] = self.pool.get('ir.sequence').get_id(cr, uid, sequence_code_or_id = warehouse_obj.purchase_sequence_id.id ) or '/'
                else:
                    vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order') or '/'
            else:
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order') or '/'
        order =  super(purchase_order, self).create(cr, uid, vals, context=context)
        return order
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        origin_po = self.pool.get('purchase.order').browse(cr, uid, id)
        warehouse_obj = origin_po.warehouse_id or False
        if warehouse_obj and warehouse_obj.purchase_sequence_id:
            context['purchase_sequence'] = True
            default.update({
                'name' : self.pool.get('ir.sequence').get_id(cr, uid, sequence_code_or_id = warehouse_obj.purchase_sequence_id.id )
            })
        else:
            default.update({
                'name' : self.pool.get('ir.sequence').get(cr, uid, 'purchase.order')
            })
        return super(purchase_order, self).copy(cr, uid, id, default, context)