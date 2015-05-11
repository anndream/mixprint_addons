# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD,. PART. (<http://www.ineco.co.th>).
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

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
#import time
#import pooler

#from tools.translate import _
#from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import decimal_precision as dp
#import netsvc

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context=context)
        if order_line.account_analytic_id:
            res['account_analytic_id'] = order_line.account_analytic_id.id
        return res
    
    
class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _columns = {
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),                        
    }
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
