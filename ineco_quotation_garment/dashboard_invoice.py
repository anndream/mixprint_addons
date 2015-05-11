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


#import datetime
#import math
#import openerp
from openerp.osv import osv, fields
from openerp import tools
#from openerp import SUPERUSER_ID
#import re
#import tools
#from tools.translate import _
#import logging
#import pooler
#import pytz
#from lxml import etree

class ineco_invoice_uncorrect(osv.osv):
    _name = 'ineco.invoice.uncorrect'
    _auto = False
    _columns = {
        'name': fields.char('Garment Order No', size=64),
        'sale_amount': fields.float('Sale Amount', digits=(12,2)),
        'invoice_list': fields.char('Invocie Lists', size=254),
        'record_count': fields.integer('Counts'),
        'invoice_amount': fields.float('Invoice Amount', digits=(12,2)),
    }
    _order = 'name'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_invoice_uncorrect')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_invoice_uncorrect AS
            select 
              so.id, 
              so.garment_order_no as name,
              so.amount_untaxed as sale_amount,
              (select array( select distinct number from account_invoice ai2 where ai2.garment_order_no = so.garment_order_no and ai2.state not in ('cancel') )) as invoice_list,
              count(*) as record_count,
              sum(ai.amount_untaxed) as invoice_amount
            from 
              sale_order so
              join account_invoice ai on ai.garment_order_no = so.garment_order_no
            where
              ai.amount_untaxed > so.amount_untaxed
              and so.state not in ('cancel')
              and so.garment_order_no is not null
              and extract(year from so.garment_order_date) >= 2015 and ai.corrected = False
            group by
              so.id,
              so.garment_order_no,
              so.amount_untaxed
        """)

class ineco_sale_invoice_balance(osv.osv):
    _name = "ineco.sale.invoice.balance"
    _auto = False
    _columns = {
        'so_id': fields.many2one('sale.order','Sale Order'),
        'garment_order_no': fields.char('MO', size=64),
        'garment_order_date': fields.date('MO Date',), 
        'sale_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'sale_amount': fields.integer('Sale Amount',),        
        'invoice_amount': fields.integer('Invoice Amount',),        
    }
    _order = 'garment_order_no'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_invoice_balance')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_invoice_balance AS
            select 
              so.id,
              so.id as so_id,
              so.garment_order_no,
              so.garment_order_date,
              so.user_id as sale_id,
              partner_id, 
              so.amount_untaxed as sale_amount,
              coalesce((select sum(amount_untaxed) from account_invoice where origin like '%' || so.name || '%' and state not in ('cancel')),0) as invoice_amount
            from 
              sale_order so
              left join res_partner rp on rp.id = so.partner_id
            where
              so.create_date > '2013-10-31'
              and so.amount_untaxed <> coalesce((select sum(amount_untaxed) from account_invoice where origin like '%' || so.name || '%' and state not in ('cancel')),0) 
              and so.state not in ('draft','cancel')
              and so.garment_order_no is not null
            order by so.garment_order_no        
        """)
        
class ineco_sale_audit_delivery(osv.osv):
    _name = 'ineco.sale.audit.delivery'
    _auto = False
    _columns = {
        'garment_order_no': fields.char('Garment Order No', size=32),
        'amount_untaxed': fields.float('Sale Amount'),
        'invoice_amount_untaxed': fields.float('Invoice Amount'),
        'name': fields.char('Picking No', size=32),
        'batch_no': fields.integer('Batch No'),
        'sale_quantity': fields.integer('Sale Qty'),
        'delivery_quantity': fields.integer('Delivery Qty'),
    }
    _order = 'garment_order_no'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_audit_delivery')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_audit_delivery AS
            select 
              sp.id,
              garment_order_no,
              amount_untaxed,
              (select coalesce(sum(amount_untaxed),0.00) from account_invoice 
               where account_invoice.garment_order_no = so.garment_order_no and
                 type = 'out_invoice' and
                 state not in ('cancel')) as invoice_amount_untaxed,
              sp.name,
              sp.batch_no,
              (select sum(product_uom_qty) from sale_order_line
               join product_product pp on pp.id = sale_order_line.product_id
               join product_template pt on pt.id = pp.product_tmpl_id
               where order_id = so.id and pt.type not in ('service')
              ) as sale_quantity,
              case 
                when sp.type = 'in' then -sp.quantity
                when sp.type = 'out' then sp.quantity
                else 
                  sp.quantity
              end as delivery_quantity
            from 
              sale_order so
              left join stock_picking sp on sp.sale_id = so.id
            where 
              extract(year from garment_order_date) >= 2015
              and so.state not in ('cancel')
              and sp.type not in ('internal')
              and sp.invoice_state = '2binvoiced'
              and so.amount_untaxed > 0
            order by
               so.garment_order_no,
               sp.batch_no
        """)
        