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
import time
#import pooler
from openerp.tools.translate import _
#from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import decimal_precision as dp
#import netsvc
import re

class account_invoice(osv.osv):
 
    def get_close_sale_no(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        sql = """
            select sale_close_no from sale_order where name = '%s' 
        """
        for data in self.browse(cr, uid, ids):
            sale_close_no = False
            if data.origin:
                docs = re.findall(r':[\w-]+[\w_]+[\w/]+',data.origin) or [data.origin]
                cr.execute(sql % (docs[0]).replace(':',''))
                sale_data = cr.dictfetchone()
                if sale_data:
                    sale_close_no = sale_data['sale_close_no']
            res[data.id] = sale_close_no
        return res
        
    _inherit = "account.invoice"
    _columns = {
        'close_sale_no': fields.function(get_close_sale_no, type='char', size=64, string="Sale Close No", readonly=True),
    }
    
    def button_close_sale(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for id in ids:
            invoice = self.browse(cr,uid,[id])[0]
            if invoice:
                child_ids = self.pool.get('res.partner').search(cr, uid, [('parent_id','child_of',invoice.partner_id.id)])
                child_ids.append(invoice.partner_id.id)
                sale_ids = self.pool.get('sale.order').search(cr, uid, [('partner_id','in',child_ids),('sale_close_no','=',False)])
                if sale_ids:
                    next_no = self.pool.get('ir.sequence').get(cr, uid, 'ineco.sale.close') or False
                    self.pool.get('sale.order').write(cr, uid, sale_ids, {'sale_close_no': next_no})

        return True    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: