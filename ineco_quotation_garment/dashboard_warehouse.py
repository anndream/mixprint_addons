# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO Ltd.,Part. (<http://www.ineco.co.th>).
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

from openerp.osv import osv, fields
from openerp import tools

class ineco_dashboard_order_late(osv.osv):
    _name = 'ineco.dashboard.order.late'
    _description = 'Order Late'
    _auto = False
    _columns = {
        'sale_order_id': fields.many2one('sale.order', 'Sale Order'),
        'garment_order_date': fields.date('Garment Order Date'),
        'garment_order_no': fields.char('Garment Order No', size=64),
        'partner_id': fields.many2one('res.partner','Customer'),
        'user_id': fields.many2one('res.users','Sales'),
        'delay': fields.integer('Delay'),
        'quantity_order': fields.integer('Order Qty'),
        'quantity_delivery': fields.integer('Delivery Qty'),
        'quantity_balance': fields.integer('Balance'),
        'do_plan': fields.integer('Plan'),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_dashboard_order_late')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_dashboard_order_late AS
select 
  sale_order.id,
  sale_order.id as sale_order_id,
  sale_order.garment_order_date,
  sale_order.garment_order_no,
  sale_order.partner_id,
  sale_order.user_id,
  extract(day from now() - date_delivery) as delay,
  round((select sum(product_uom_qty) from sale_order_line 
     join product_product pp on pp.id = sale_order_line.product_id
     join product_template pt on pt.id = pp.product_tmpl_id
         where order_id = sale_order.id and pt.type <> 'service')) as quantity_order,
  round((select sum(quantity) from stock_picking sp
         where sp.sale_id = sale_order.id and sp.state in  ('done','cancel') and sp.type = 'out')) as quantity_delivery,
  round((select sum(product_uom_qty) from sale_order_line 
     join product_product pp on pp.id = sale_order_line.product_id
     join product_template pt on pt.id = pp.product_tmpl_id
         where order_id = sale_order.id and pt.type <> 'service')) - 
  round((select coalesce(sum(quantity),0) from stock_picking sp
         where sp.sale_id = sale_order.id and sp.state in  ('done','cancel') and sp.type = 'out')) as quantity_balance,
  date_delivery - garment_order_date as do_plan

from sale_order
where garment_order_date >= '2014-01-01'
    and state not in ('cancel')
    and extract( day from case when (select max(date_done) from stock_picking sp
             where sp.sale_id = sale_order.id and sp.state in  ('done','cancel') and sp.type = 'out') is null then date_delivery - now()
           else 
            (select max(date_done) from stock_picking sp
             where sp.sale_id = sale_order.id and sp.state in  ('done','cancel') and sp.type = 'out') - date_delivery
    end) < 0
    /*and round((select sum(product_uom_qty) from sale_order_line
               join product_product pp on pp.id = sale_order_line.product_id
           join product_template pt on pt.id = pp.product_tmpl_id
               where order_id = sale_order.id and pt.type <> 'service')) > round((select coalesce(sum(quantity),0) from stock_picking sp
   where sp.sale_id = sale_order.id and sp.state in ('done','cancel') and sp.type = 'out'))*/
order by
   date_delivery            

        """)
        
class ineco_dashboard_order_late_summary(osv.osv):
    _name = 'ineco.dashboard.order.late.summary'
    _description = 'Order Late Summary'
    _auto = False
    _columns = {
        'year': fields.char('Year', size=4),
        'month': fields.integer('Month',),
        'order_total': fields.integer('Order Total'),
        'order_count': fields.integer('Order Count'),
        'order_late_count': fields.integer('Late'),
        'order_done_count': fields.integer('Done'),
        'order_late_percent': fields.float('Late (%)', digits=(12,2)),
        'order_done_percent': fields.float('Done (%)', digits=(12,2)),
        'order_late_avg': fields.integer('Avg'),
        'order_late_max': fields.integer('Max'),
        'order_late_min': fields.integer('Min'),
        'order_progress_count': fields.integer('Progress'),
        'order_progress_percent': fields.float('Progress (%)', digits=(12,2)),        
    }
    _order = 'year,month'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_dashboard_order_late_summary')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_dashboard_order_late_summary AS
select
  replace(min(garment_order_date)::text,'-','')::integer as id,
  extract(year from garment_order_date)::text as year,
  extract(month from garment_order_date) as month,
  sum(quantity_order)::integer as order_total,
  count(*) as order_count,
  abs(count(case when delay < 0 then 1 else null end)) as order_late_count,
  count(case when delay >= 0 and quantity_balance = 0 then 1 else null end) as order_done_count,
  abs(count(case when delay < 0 then 1 else null end)) * 100 / count(*) as order_late_percent,
  count(case when delay >= 0 and quantity_balance = 0 then 1 else null end) * 100 / count(*) as order_done_percent,
  abs(coalesce(avg(case when delay < 0 then delay else null end), 0.0)::integer) as order_late_avg,
  abs(coalesce(min(case when delay < 0 then delay else null end), 0.0)::integer) as order_late_max,
  abs(coalesce(max(case when delay < 0 then delay else null end), 0.0)::integer) as order_late_min,
  count(*) -
    abs(count(case when delay < 0 then 1 else null end)) -
    count(case when delay >= 0 and quantity_balance = 0 then 1 else null end) as order_progress_count,
  (count(*) -
    abs(count(case when delay < 0 then 1 else null end)) -
    count(case when delay >= 0 and quantity_balance = 0 then 1 else null end)) * 100 / count(*) as order_progress_percent      
from (
    select
      garment_order_no,
      garment_order_date,
      date_delivery,
      extract(day from 
      case when (select max(date_done) from stock_picking sp
             where sp.sale_id = sale_order.id and sp.state in  ('done','cancel') and sp.type = 'out') is null then date_delivery - now()  
           else 
            (select max(date_done) from stock_picking sp
             where sp.sale_id = sale_order.id and sp.state in  ('done','cancel') and sp.type = 'out') - date_delivery 
      end) as delay,
      round((select sum(product_uom_qty) from sale_order_line 
         join product_product pp on pp.id = sale_order_line.product_id
         join product_template pt on pt.id = pp.product_tmpl_id
         where order_id = sale_order.id and pt.type <> 'service')) as quantity_order,
      round((select coalesce(sum(product_uom_qty),0) from sale_order_line 
         join product_product pp on pp.id = sale_order_line.product_id
         join product_template pt on pt.id = pp.product_tmpl_id
         where order_id = sale_order.id and pt.type <> 'service')) - 
      round((select coalesce( sum(quantity), 0) from stock_picking sp
         where sp.sale_id = sale_order.id and sp.state in  ('done','cancel') and sp.type = 'out')) as quantity_balance  
    from 
      sale_order
    where
      state not in ('cancel')
      and garment_order_date >= '2014-01-01'
) sale_list
group by
  extract(year from garment_order_date),
  extract(month from garment_order_date)            
            
        """)
    