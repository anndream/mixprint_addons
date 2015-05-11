# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITE (<http://www.ineco.co.th>).
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

#import time
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
#from operator import itemgetter

#import logging
#import openerp.pooler
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _

#from openerp.tools.float_utils import float_round
#from openerp import SUPERUSER_ID
#import openerp.tools

class ineco_import_account_invoice(osv.osv):
    _name = 'ineco.import.account.invoice'
    _columns = {
        'name': fields.char('Description', size=128),
        'line_ids': fields.one2many('ineco.import.account.invoice.line', 'job_id', 'Lines'),
    }
    
class ineco_import_account_invoice_line(osv.osv):
    _name = 'ineco.import.account.invoice.line'
    _columns = {
        'name': fields.char('Supplier Invoice Number', size=64, required=True),
        'date': fields.char('Date', size=12, required=True),
        'date_ok': fields.date('Invoice Date'),
        'supplier': fields.char('Supplier', size=254, required=True),
        'partner_id': fields.many2one('res.partner','Partner'),
        'product': fields.char('Product', size=254, required=True),
        'product_id': fields.many2one('product.product','Product'),
        'type': fields.selection([('I','Included Vat'),('E','Excluded Vat')], 'Vat Type'),
        'vat': fields.float('Vat', digits_compute=dp.get_precision('Account')),
        'total': fields.float('Total', digits_compute=dp.get_precision('Account')),
        'job_id': fields.many2one('ineco.import.account.invoice', 'Invoice'),
    }