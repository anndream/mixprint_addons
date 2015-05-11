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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import time
from openerp.osv import fields, osv
#import openerp.decimal_precision as dp
from openerp.tools.translate import _

class iyara_lc(osv.osv):
    _name = 'iyara.lc'
    _description = "LC Table"
    _columns = {
        'name': fields.char('LC Number', size=32, required=True),
        'proforma_invoice_no': fields.char('Proforma Invoice No', size=32, ),
        'date': fields.date('Date Issue'),
        'partner_bank_id':fields.many2one('res.partner', 'Bank Name',  domain=[('bank_lc','=',True)],required=True,),                    
        'total': fields.float('USD'),
        'currency_id': fields.many2one('res.currency','Currency',required=True),
        'available': fields.float('Available'),
        'date_tr': fields.date('Date TR'),
        'date_due': fields.date('Date Due'),
        'date_etd': fields.date('Date ETD'), 
        'date_eta': fields.date('Date ETA'),
        'date_import': fields.date('To Warehouse Iyara Date'),                      
        'line_ids': fields.one2many('iyara.lc.line', 'lc_id', 'LC Lines',), 
        'note': fields.text('Note'),                            
    }
    
class ineco_lc_line(osv.osv):
    _name = 'iyara.lc.line'
    _description = 'LC Line'
    _columns = {
        'lc_id': fields.many2one('iyara.lc', 'LC'),   
        'purchase_line': fields.many2one('purchase.order.line','Purchase Line',domain=[('lc','=',True),('line_ids','=',False),('state','not in',('draft','cancel'))],required=True,),                                                             
        'purchase_id': fields.related('purchase_line','order_id',type='many2one',relation='purchase.order',string='Purchase Order',readonly=True),        
        'product_id': fields.related('purchase_line','product_id',type='many2one',relation='product.product',string='Gen Model',readonly=True),        
        'product_qty': fields.related('purchase_line','product_qty',type='float',string='Qty',readonly=True),
        'price_subtotal': fields.related('purchase_line','price_subtotal',type='float',string='Subtotal',readonly=True),
        'project_id': fields.related('purchase_line','account_analytic_id',type='many2one',relation='account.analytic.account',string='Project',readonly=True),
        'sale_id': fields.related('project_id','manager_id',type='many2one',relation='res.users',string='Sale',readonly=True),
        'categ_id': fields.related('product_id','categ_id',type='many2one',relation='product.category',string='GEN',readonly=True),              
        'date_finish': fields.date('Finish Date'),            
    }
    
class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'
    _columns = {
                'lc': fields.related('partner_id','supplier_lc',type='boolean',string='LC',readonly=True),               
                'line_ids': fields.one2many('iyara.lc.line', 'purchase_line', 'LC Lines',), 
    }      
    
class res_partner(osv.osv):

    _inherit = 'res.partner'
    _columns = {
                'bank_lc': fields.boolean('Bank LC',), 
                'supplier_lc': fields.boolean('Supplier LC',),                   
    }    
    _defaults = {
        'bank_lc': lambda *a: 0,
        'supplier_lc': lambda *a: 0,
    }        
    
    
    