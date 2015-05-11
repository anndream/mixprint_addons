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

from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
#import time
#from openerp import pooler
from openerp.osv import fields, osv
#from openerp.tools.translate import _
#from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import openerp.addons.decimal_precision as dp
#from openerp import netsvc

class sale_order(osv.osv):
    
    def _get_saledate(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'sale_year': 0,
                'sale_month': 0,
            }
            if order.date_order:
                so_date = datetime.strptime(order.date_order, '%Y-%m-%d')
                res[order.id]['sale_year'] = so_date.year
                res[order.id]['sale_month'] = '%.2d' % so_date.month
        return res
            
    _inherit = "sale.order"
    _description = "Add Year/Month Function Field"
    _columns = {
        'sale_year': fields.function(_get_saledate, type='char', string='Year',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
            multi='sums', track_visibility='always'),                
        'sale_month': fields.function(_get_saledate, type='char', string='Month',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
            multi='sums', track_visibility='always'),                
    }
    
    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = '/'
        default['message_ids'] = []
        return super(sale_order, self).copy(cr, uid, ids, default, context=context)    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
