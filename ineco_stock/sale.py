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

from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class sale_shop(osv.osv):
    _inherit = "sale.shop"
    _description = "Add Auto Sequence, Stock Journal"
    _columns = {
        'sequence_id': fields.many2one('ir.sequence', 'Sale Order Sequence'),
        'production_sequence_id': fields.many2one('ir.sequence', 'Production Sequence'),
        'stock_journal_id': fields.many2one('stock.journal','Stock Journal'),
    }
    
class sale_order(osv.osv):
    
    _inherit = 'sale.order'
        
    def _prepare_order_picking(self, cr, uid, order, context=None):
        if order.shop_id.stock_journal_id and order.shop_id.stock_journal_id.sequence_id:
            pick_name = self.pool.get('ir.sequence').get_id(cr, uid, sequence_code_or_id=order.shop_id.stock_journal_id.sequence_id.id )
            #pick_name = self.pool.get('ir.sequence').get(cr, uid, order.shop_id.stock_journal_id.sequence_id.code)
        else:
            pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'stock_journal_id': order.shop_id.stock_journal_id and order.shop_id.stock_journal_id.id or False,
            'name': pick_name,
            'origin': order.name,
            'date': order.date_order,
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
        }    