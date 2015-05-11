# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITED (<http://www.ineco.co.th>).
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

class ineco_sale_summary2(osv.osv):
    _name = 'ineco.sale.summary2'
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_summary2')

        cr.execute(""" CREATE VIEW ineco_sale_summary2 AS (
            select 
              ru.id as user_id,
              (select count(*)::numeric || '/' || ltrim(to_char(sum(amount_untaxed),'999,999,990.00')) from sale_order so 
               where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                     and so.state <> 'cancel' and left(so.name,2) in ('SO','QU')
              ) as so,
              (select count(*)::numeric || '/' || ltrim(to_char(sum(amount_untaxed),'999,999,990.00')) from sale_order so 
               where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                     and so.state <> 'cancel' and left(so.name,2) in ('SO','QU')
              ) as mo,
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
               and date_part('month',now()) = date_part('month', date_closed)  
              ) as lose,  
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 1 
               and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
              ) as percent10, 
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 3   
               and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
              ) as percent50, 
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 5  
               and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
              ) as percent90     
            from 
              res_users ru
            left join res_partner rp on ru.partner_id = rp.id
            where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60)
            order by rp.name        
        )
        """)    
        
class ineco_sale_summary(osv.osv):
    _name = 'ineco.sale.summary'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'so': fields.char('SO', size=32),
        'mo': fields.char('MO', size=32),
        'lose': fields.char('Opp Lost', size=32),
        'percent10': fields.char('Opp 10%', size=32),
        'percent50': fields.char('Opp 50%', size=32),
        'percent90': fields.char('Opp 90%', size=32),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary2 from ineco_sale_summary2

                            ) as a
                    ) b
                ) c
            )""")

class ineco_sale_summary3(osv.osv):
    _name = "ineco.sale.summary3"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_summary3')
        cr.execute("""
            CREATE VIEW ineco_sale_summary3 AS (
                select 
                  ru.id as user_id,
                  (select count(*) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and date_part('year',now()) = date_part('year',so.date_sale_close)
                         and so.state <> 'cancel'
                         and left(so.name,2) in ('SO','QU')
                  ) as so1,
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and date_part('year',now()) = date_part('year',so.date_sale_close)
                         and so.state <> 'cancel'
                         and left(so.name,2) in ('SO','QU')
                  ) as so2,
                  (select count(*)::numeric  from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                        and left(so.garment_order_no,2) = 'MO'
                  ) as mo1,
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                        and left(so.garment_order_no,2) = 'MO'
                  ) as mo2,
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
                     and date_part('month',now()) = date_part('month',cl.date_closed)
                     and date_part('year',now()) = date_part('year',cl.date_closed) 
                  ) as lose1,  
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
                     and date_part('month',now()) = date_part('month',cl.date_closed)
                     and date_part('year',now()) = date_part('year',cl.date_closed) 
                  ) as lose2,  
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 1 and type = 'opportunity'
                  ) as percent101, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 1 and type = 'opportunity'
                  ) as percent102, 
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 3   
                  ) as percent501, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 3   
                  ) as percent502,               
                  (select count(*)::numeric   from crm_lead cl  
                   where user_id = ru.id and stage_id = 5  
                  ) as percent901,
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 5  
                  ) as percent902,
                  ru.nickname as nickname,
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 10   
                  ) as percent301, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 10   
                  ) as percent302,
                  (
                  select count(*) from crm_lead where type = 'opportunity'
                      and user_id = ru.id
                      and stage_id in (1,3,5,10)
                  ) as total_opportunity   
                      
                from 
                  res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and
                    ru.mixprint = True or ru.smart = True 
                    --ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    --signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                order by rp.name                
            )    
        """)
        
class ineco_sale_summary4(osv.osv):
    _name = 'ineco.sale.summary4'
    _description = "Oppportunity Stages (Mixprint)"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'so1': fields.integer('SO',),
        'so2': fields.integer('SO',),
        'mo1': fields.integer('MO',),
        'mo2': fields.integer('MO',),
        'lose1': fields.integer('Opp Lost',),
        'lose2': fields.integer('Opp Lost',),
        'percent101': fields.integer('10%',),
        'percent102': fields.integer('10%',),
        'percent501': fields.integer('50%',),
        'percent502': fields.integer('50%',),
        'percent901': fields.integer('90%',),
        'percent902': fields.integer('90%',),
        'nickname': fields.char('Nick Name', size=32),
        'percent301': fields.integer('30%',),
        'percent302': fields.integer('30%',),
        'total_opportunity': fields.integer('Total Opp',),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary4')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary4 AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary3 from ineco_sale_summary3
                                where user_id in (select id from res_users where mixprint = True)
                            ) as a
                    ) b
                ) c
            )""")

class ineco_sale_summary4smart(osv.osv):
    _name = 'ineco.sale.summary4smart'
    _description = "Oppportunity Stages (Smart)"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'so1': fields.integer('SO',),
        'so2': fields.integer('SO',),
        'mo1': fields.integer('MO',),
        'mo2': fields.integer('MO',),
        'lose1': fields.integer('Opp Lost',),
        'lose2': fields.integer('Opp Lost',),
        'percent101': fields.integer('10%',),
        'percent102': fields.integer('10%',),
        'percent501': fields.integer('50%',),
        'percent502': fields.integer('50%',),
        'percent901': fields.integer('90%',),
        'percent902': fields.integer('90%',),
        'nickname': fields.char('Nick Name', size=32),
        'percent301': fields.integer('30%',),
        'percent302': fields.integer('30%',),
        'total_opportunity': fields.integer('Total Opp',),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary4smart')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary4smart AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary3 from ineco_sale_summary3
                                where user_id in (select id from res_users where smart = True)
                            ) as a
                    ) b
                ) c
            )""")
        
class ineco_sale_summary5_query(osv.osv):
    _name = "ineco.sale.summary5.query"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_summary5_query')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_summary5_query AS (
                select 
                  ru.id as user_id,
                  ru.nickname,
                  /*(select count(*) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and so.state <> 'cancel'
                  ) as so1,*/
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and date_part('year',now()) = date_part('year',so.date_sale_close)
                         and so.state <> 'cancel'
                         and left(so.name,2) in ('SO','QU')
                  ) as so2,
                  /*
                  (select count(*)::numeric  from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                  ) as mo1,*/
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                        and left(so.garment_order_no,2) = 'MO'
                  ) as mo2,
                  (
                    select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id
                  ) as total_customer,
                  (
                    select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id and is_company = true
                  ) as total_customer_company,            
                  (
                    select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id and date_part('month',now()) = date_part('month', res_partner.create_date)
                        and date_part('year',now()) = date_part('year', res_partner.create_date)
                  ) as total_customer_new,
                  (select coalesce(count(*),0) from crm_phonecall cp
            left join crm_case_categ ccc on cp.categ_id = ccc.id
            where ccc.id = 9 and date_part('month',now()) = date_part('month', cp.create_date)
                        and date_part('year',now()) = date_part('year', cp.create_date)  
                        and cp.user_id = ru.id
                  ) as logcall_inbound,
                  (select coalesce(count(*),0) from crm_phonecall cp
            --left join crm_case_categ ccc on cp.categ_id = ccc.id
            where (cp.categ_id is null or cp.categ_id = 10) and date_part('month',now()) = date_part('month', cp.create_date)
                        and date_part('year',now()) = date_part('year', cp.create_date)  
                        and cp.user_id = ru.id
                  ) as logcall_outbound,
                  (select coalesce(count(*),0) from crm_phonecall cp
            left join crm_case_categ ccc on cp.categ_id = ccc.id
            where cp.visit = true and date_part('month',now()) = date_part('month', cp.create_date)
                        and date_part('year',now()) = date_part('year', cp.create_date)  
                        and cp.user_id = ru.id
                  ) as logcall_visit,
                  (
                    select count(*) from sale_order where state <> 'cancel'  and user_id = ru.id
                        and date_part('month',now()) = date_part('month', sale_order.date_sale_close)
                        and date_part('year',now()) = date_part('year', sale_order.date_sale_close)  
                  ) as total_quotation,
                  (
                    select count(*) from sale_order where state in ('manual','send')  and user_id = ru.id
                        and date_part('month',now()) = date_part('month', sale_order.date_sale_close)
                        and date_part('year',now()) = date_part('year', sale_order.date_sale_close)  
                  ) as total_quotation_saleorder,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 1 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_pc,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 2 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_ds,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 3 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_rp,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 4 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_mp,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 5 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_fr
                from 
                  res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and 
                   ru.mixprint = True or ru.smart = True
                   --ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                   --signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                order by rp.name      
        )    
        """)
        
class ineco_sale_summary5(osv.osv):
    _name = 'ineco.sale.summary5'
    _description = "Sale Log (Mixprint)"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'nickname': fields.char('Nick Name', size=32),
        'so2': fields.integer('SO',),
        'mo2': fields.integer('MO',),
        'total_customer': fields.integer('Total',),
        'total_customer_company': fields.integer('Company',),
        'total_customer_new': fields.integer('New',),
        'logcall_inbound': fields.integer('In',),
        'logcall_outbound': fields.integer('Out',),
        'logcall_visit': fields.integer('Visit',),
        'total_quotation': fields.integer('QO',),
        'total_quotation_saleorder': fields.integer('SO',),
        'total_picking_pc': fields.integer('PC',),
        'total_picking_ds': fields.integer('DS',),
        'total_picking_rp': fields.integer('PR',),
        'total_picking_mp': fields.integer('PM',),
        'total_picking_fr': fields.integer('PF',),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary5')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary5 AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary5_query from ineco_sale_summary5_query
                                where user_id in (select id from res_users where mixprint = True)
                            ) as a
                    ) b
                ) c
            )""")        
        
class ineco_sale_summary5smart(osv.osv):
    _name = 'ineco.sale.summary5smart'
    _description = "Sale Log (Smart)"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'nickname': fields.char('Nick Name', size=32),
        'so2': fields.integer('SO',),
        'mo2': fields.integer('MO',),
        'total_customer': fields.integer('Total',),
        'total_customer_company': fields.integer('Company',),
        'total_customer_new': fields.integer('New',),
        'logcall_inbound': fields.integer('In',),
        'logcall_outbound': fields.integer('Out',),
        'logcall_visit': fields.integer('Visit',),
        'total_quotation': fields.integer('QO',),
        'total_quotation_saleorder': fields.integer('SO',),
        'total_picking_pc': fields.integer('PC',),
        'total_picking_ds': fields.integer('DS',),
        'total_picking_rp': fields.integer('PR',),
        'total_picking_mp': fields.integer('PM',),
        'total_picking_fr': fields.integer('PF',),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary5smart')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary5smart AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary5_query from ineco_sale_summary5_query
                                where user_id in (select id from res_users where smart = True)
                            ) as a
                    ) b
                ) c
            )""")        
        
class ineco_sale_qty_amount_temp(osv.osv):
    _name = "ineco.sale.qty.amount.temp"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_amount_query')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_qty_amount_query AS (
                select
                    ru.id as user_id,
                    '1. SO' as type,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('cancel','draft') ) as qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('draft', 'cancel') ) as amount,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('draft','cancel') ) as ytd_qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('draft','cancel') ) as ytd_amount
                from 
                    res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'                
                union
                select
                    ru.id as user_id,
                    '2. MO' as type,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as amount,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as ytd_qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as ytd_amount
                from 
                    res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                    
                order by user_id, type      
            )               
            """)
    
class ineco_sale_qty_amount(osv.osv):
    _name = 'ineco.sale.qty.amount'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'type': fields.char('Type',size=32),
        'qty': fields.integer('Qty',),
        'amount': fields.integer('Amount',),
        'ytd_qty': fields.integer('Year Qty',),
        'ytd_amount': fields.integer('Year Amount',),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_amount')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_qty_amount AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_qty_amount_query from ineco_sale_qty_amount_query
                            ) as a
                    ) b
                ) c
            )""")     
        
class ineco_sale_qty_customer_temp(osv.osv):
    _name = "ineco.sale.qty.customer.temp"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_customer_query')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_qty_customer_query AS (        
select 
  ru.id as user_id,
  '1. New' as type,
  (select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id and date_part('month',now()) = date_part('month', res_partner.create_date)
                        and date_part('year',now()) = date_part('year', res_partner.create_date)
  ) as customer_total 
from 
    res_users ru
    left join res_partner rp on ru.partner_id = rp.id
where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
union
select 
  ru.id as user_id,
  '3. Total' as type,
  (select count(*) from res_partner where user_id = ru.id and active = true) as customer_total 
from 
    res_users ru
    left join res_partner rp on ru.partner_id = rp.id
where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
union
select 
  ru.id as user_id,
  '2. Company' as type,
  (select count(*) from res_partner where user_id = ru.id and active = true and is_company = true) as customer_total 
from 
    res_users ru
    left join res_partner rp on ru.partner_id = rp.id 
where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'

order by user_id, type        
           )
        """)
        
class ineco_sale_qty_customer(osv.osv):
    _name = "ineco.sale.qty.customer"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'type': fields.char('Type',size=32),
        'customer_total': fields.integer('Quantity',),        
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_customer')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_qty_customer AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_qty_customer_query from ineco_sale_qty_customer_query
                            ) as a
                    ) b
                ) c
        )""")

class ineco_sale_mytop_opportunity_temp(osv.osv):
    _name = "ineco.sale.mytop.opportunity.temp"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_mytop_opportunity_temp')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_mytop_opportunity_temp AS (
                select 
                  cl.user_id, 
                  cl.partner_id, 
                  stage_id, 
                  planned_revenue, 
                  cl.last_date_count, 
                  rp.last_date_count as last_contact_date 
                from crm_lead cl
                left join res_users ru on ru.id = user_id
                left join res_partner rp on rp.id = cl.partner_id
                where 
                    cl.type = 'opportunity' and ru.active = true
                    and cl.state not in ('done','cancel')            
        )""")

#                select user_id, cl.partner_id, stage_id, planned_revenue, last_date_count, last_contact_date 
#                from crm_lead cl
#                left join res_users ru on ru.id = user_id
#                where type = 'opportunity' and ru.active = true
#                  and state not in ('done','cancel')                        

class ineco_sale_mytop_opportunity(osv.osv):
    _name = "ineco.sale.mytop.opportunity"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
    }
    _order = 'planned_revenue desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_mytop_opportunity')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_mytop_opportunity AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_mytop_opportunity_temp from ineco_sale_mytop_opportunity_temp
                            ) as a
                    ) b
                ) c
        )""")
    
class ineco_sale_all_opportunity(osv.osv):
    _name = "ineco.sale.all.opportunity"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_all_opportunity')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_all_opportunity AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, t1.last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on t1.partner_id = rp.id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state not in ('done','cancel')
                   order by planned_revenue desc limit 50)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state not in ('done','cancel') and ru.active = true
                order by user_id, planned_revenue desc;      
        """)
        
class ineco_sale_fix_temp(osv.osv):
    _name = "ineco.sale.fix.temp"
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_fix_temp')
        cr.execute("""
            create or replace view ineco_sale_fix_temp as 
            select 
              sp.id as property_id,
              slp.name as name,
              sol.product_id,
              sol.price_unit,
              sol.product_uom_qty,
              sol.product_uom,
              so.id as order_id,
              so.garment_order_no,
              so.note,
              so.date_order,
              so.garment_order_date,
              so.partner_id
            from sale_line_property slp
            join sale_property sp on slp.property_id = sp.id
            join sale_order_line sol on slp.sale_line_id = sol.id
            join sale_order so on sol.order_id = so.id
            join product_product pp on pp.id = sol.product_id
            join product_template pt on pt.id = pp.product_tmpl_id
            where so.state not in ('draft','cancel') 
              and (sp.name like '%ซ่อม%' or sp.name like '%แผนก   %')
              and so.shop_id = 2
          """)
        
class ineco_sale_fix(osv.osv):
    _name = "ineco.sale.fix"
    _auto = False
    _columns = {
        'property_id': fields.many2one('sale.property','Property',readonly=True),
        'name': fields.char('Description',size=254,readonly=True),
        'product_id': fields.many2one('product.product','Product',readonly=True),
        'price_unit': fields.float('Price Unit',readonly=True),
        'product_uom_qty': fields.float('Quantity',readonly=True),
        'product_uom': fields.many2one('product.uom','UOM',readonly=True),
        'order_id': fields.many2one('sale.order','Sale Order', readonly=True),
        'garment_order_no': fields.char('MO No', size=64, readonly=True),
        'note': fields.text('Note',readonly=True),
        'date_order': fields.date('Date Order',readonly=True),
        'garment_order_date': fields.date('Date Mo', readonly=True),
        'partner_id': fields.many2one('res.partner','Customer',readonly=True),
    }
    _order = 'garment_order_no desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_fix')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_fix AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_fix_temp from ineco_sale_fix_temp
                            ) as a
                    ) b
                ) c
        )""")

        
class ineco_sale_lose_opportunity(osv.osv):
    _name = "ineco.sale.lose.opportunity"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
        'opportunity_cost_ids': fields.one2many('ineco.opportunity.cost','opportunity_id','Costs'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on t1.partner_id = rp.id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
              and extract(year from b.date_lose) = extract(year from now())
              and extract(month from b.date_lose) = extract(month from now())
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
               and extract(year from t1.date_lose) = extract(year from now())
               and extract(month from t1.date_lose) = extract(month from now())
                order by user_id, planned_revenue desc;       
        """)
        
class ineco_sale_lose_opportunity_month1(osv.osv):
    _name = "ineco.sale.lose.opportunity.month1"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
        'opportunity_cost_ids': fields.one2many('ineco.opportunity.cost','opportunity_id','Costs'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity_month1')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity_month1 AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on t1.partner_id = rp.id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
                     and b.date_lose between cast(date_trunc('month', current_date) as date) - interval '1 months' and cast(date_trunc('month', current_date) as date) - interval '1 days'
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
                   and t1.date_lose between cast(date_trunc('month', current_date) as date) - interval '1 months' and cast(date_trunc('month', current_date) as date) - interval '1 days'
                order by user_id, planned_revenue desc;            
        """)     
        
class ineco_sale_lose_opportunity_month3(osv.osv):
    _name = "ineco.sale.lose.opportunity.month3"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
        'opportunity_cost_ids': fields.one2many('ineco.opportunity.cost','opportunity_id','Costs'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity_month3')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity_month3 AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on rp.id = t1.partner_id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
                     and b.date_lose between cast(date_trunc('month', current_date) as date) - interval '3 months' and cast(date_trunc('month', current_date) as date) - interval '1 months'
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
                   and t1.date_lose between cast(date_trunc('month', current_date) as date) - interval '3 months' and cast(date_trunc('month', current_date) as date) - interval '1 months'
                order by user_id, planned_revenue desc;            
        """)              

class ineco_sale_lose_opportunity_month6(osv.osv):
    _name = "ineco.sale.lose.opportunity.month6"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
        'opportunity_cost_ids': fields.one2many('ineco.opportunity.cost','opportunity_id','Costs'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity_month6')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity_month6 AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
                left join res_partner rp on rp.id = t1.partner_id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
                     and b.date_lose between cast(date_trunc('month', current_date) as date) - interval '6 months' and cast(date_trunc('month', current_date) as date) - interval '3 months'
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
                   and t1.date_lose between cast(date_trunc('month', current_date) as date) - interval '6 months' and cast(date_trunc('month', current_date) as date) - interval '3 months'
                order by user_id, planned_revenue desc;         
        """)        
        
class ineco_delivery_cost_dashboard(osv.osv):
    _name = 'ineco.delivery.cost.dashboard'
    _auto = False
    _columns = {
        'name': fields.char('Document Name', size=32, readonly=True),
        'date': fields.datetime('Document Date', readonly=True),
        'year': fields.integer('Year', readonly=True),
        'month': fields.integer('Month', readonly=True),
        'day': fields.integer('Day', readonly=True),
        'origin': fields.char('Origin', readonly=True),
        'partner_id': fields.many2one('res.partner','Customer',readonly=True),
        'stock_journal_id': fields.many2one('stock.journal','Journal',readonly=True),
        'batch_no': fields.integer('Batch No',readonly=True),
        'product_qty': fields.integer('Product Qty',readonly=True),
        'state': fields.char('State', size=32,readonly=True),
        'cost_type_id': fields.many2one('ineco.cost.type','Cost Type',readonly=True),
        'cost_qty': fields.integer('Quantity',readonly=True),
        'cost': fields.float('Cost',readonly=True),
        'amount': fields.float('Amount',readonly=True),
    }      

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_delivery_cost_dashboard')
        cr.execute("""
            CREATE VIEW ineco_delivery_cost_dashboard AS
                select 
                  sp.id + ict.id as id,
                  sp.name, 
                  sp.date, 
                  extract(year from sp.date) as year, 
                  extract(month from sp.date) as month, 
                  extract(day from sp.date) as day, 
                  sp.origin, sp.partner_id, sp.stock_journal_id, sp.batch_no, 
                  sp.ineco_date_delivery as date_delivery, 
                  round(sp.quantity) as product_qty, 
                  sp.state,
                  ict.id as cost_type_id,
                  coalesce(ipc.quantity,0) as cost_qty,
                  coalesce(ipc.cost,0.00) as cost,
                  coalesce(ipc.quantity * ipc.cost,0.00) as amount
                from stock_picking sp
                join ineco_picking_cost ipc on ipc.picking_id = sp.id
                join ineco_cost_type ict on ict.id = ipc.cost_type_id
                where sp.type = 'out'
                order by sp.date
        """)
        
class ineco_sale_amount_dashboard_temp(osv.osv):
    _name = 'ineco.sale.amount.dashboard.temp'
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_amount_dashboard_temp')
        cr.execute(""" CREATE VIEW ineco_sale_amount_dashboard_temp AS 
            select 
              ru.id as user_id, 
              --rp.name, 
              calendar.year,
              --Januaray
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 1
                 and user_id = ru.id),0.00) as jan_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 1
                 and user_id = ru.id),0.00) as jan_garment_amount,
              --Febuaray
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 2
                 and user_id = ru.id),0.00) as feb_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 2
                 and user_id = ru.id),0.00) as feb_garment_amount,       
              --March
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 3
                 and user_id = ru.id),0.00) as mar_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 3
                 and user_id = ru.id),0.00) as mar_garment_amount,       
              --April
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 4
                 and user_id = ru.id),0.00) as apr_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 4
                 and user_id = ru.id),0.00) as apr_garment_amount,       
              --May
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 5
                 and user_id = ru.id),0.00) as may_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 5
                 and user_id = ru.id),0.00) as may_garment_amount,       
              --June
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 6
                 and user_id = ru.id),0.00) as jun_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 6
                 and user_id = ru.id),0.00) as jun_garment_amount,       
              --July
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 7
                 and user_id = ru.id),0.00) as jul_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 7
                 and user_id = ru.id),0.00) as jul_garment_amount,       
              --August
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 8
                 and user_id = ru.id),0.00) as aug_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 8
                 and user_id = ru.id),0.00) as aug_garment_amount,      
              --September
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 9
                 and user_id = ru.id),0.00) as sep_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 9
                 and user_id = ru.id),0.00) as sep_garment_amount ,      
              --Octorber
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 10
                 and user_id = ru.id),0.00) as oct_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 10
                 and user_id = ru.id),0.00) as oct_garment_amount,       
              --November
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 11
                 and user_id = ru.id),0.00) as nov_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 11
                 and user_id = ru.id),0.00) as nov_garment_amount,       
              --December
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from date_sale_close) = calendar.year and
                 extract(month from date_sale_close) = 12
                 and user_id = ru.id),0.00) as dec_sale_amount,
              coalesce((select round(sum(amount_untaxed)/100000,2) from sale_order
               where extract(year from garment_order_date) = calendar.year and
                 extract(month from garment_order_date) = 12
                 and user_id = ru.id),0.00) as dec_garment_amount,
              ru.nickname 
            
            from res_users ru
            cross join 
            (SELECT 
              extract(year from generate_series(_from, _to, '1 year') ) AS year
            FROM 
              (select min(date_order) as _from, max(date_order+ interval '1 month') as _to 
               from sale_order where state not in ('draft','cancel') 
                 and extract(year from date_order) not in (1912,1956,2556)) a) calendar
            join res_partner rp on rp.id = ru.partner_id
            where
              ru.active = true
              and ru.signature like '%ขาย%'
              and calendar.year > extract(year from now()) - 3
            order by
              user_id, year
        """)
        
class ineco_sale_amount_dashboard(osv.osv):
    _name = 'ineco.sale.amount.dashboard'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users','Sale',readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'jan_sale_amount': fields.float('January',readonly=True),
        'jan_garment_amount': fields.float('January',readonly=True),
        'feb_sale_amount': fields.float('Febuary',readonly=True),
        'feb_garment_amount': fields.float('Febuary',readonly=True),
        'mar_sale_amount': fields.float('March',readonly=True),
        'mar_garment_amount': fields.float('March',readonly=True),
        'apr_sale_amount': fields.float('April',readonly=True),
        'apr_garment_amount': fields.float('April',readonly=True),
        'may_sale_amount': fields.float('May',readonly=True),
        'may_garment_amount': fields.float('May',readonly=True),
        'jun_sale_amount': fields.float('June',readonly=True),
        'jun_garment_amount': fields.float('June',readonly=True),
        'jul_sale_amount': fields.float('July',readonly=True),
        'jul_garment_amount': fields.float('July',readonly=True),
        'aug_sale_amount': fields.float('August',readonly=True),
        'aug_garment_amount': fields.float('August',readonly=True),
        'sep_sale_amount': fields.float('September',readonly=True),
        'sep_garment_amount': fields.float('September',readonly=True),
        'oct_sale_amount': fields.float('Octorber',readonly=True),
        'oct_garment_amount': fields.float('Octorber',readonly=True),
        'nov_sale_amount': fields.float('November',readonly=True),
        'nov_garment_amount': fields.float('November',readonly=True),
        'dec_sale_amount': fields.float('December',readonly=True),
        'dec_garment_amount': fields.float('December',readonly=True),
        'nickname': fields.char('Nickname',readonly=True),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_amount_dashboard')
        cr.execute(""" CREATE VIEW ineco_sale_amount_dashboard AS 
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_amount_dashboard_temp from ineco_sale_amount_dashboard_temp
                            ) as a
                    ) b
                ) c
        """)

class ineco_sale_qty_dashboard_temp(osv.osv):
    _name = 'ineco.sale.qty.dashboard.temp'
    _description = "Dashboard Sale Quantity by Polo (Smart user next_garment_order_date)"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_dashboard_temp')
        cr.execute(""" CREATE or replace VIEW ineco_sale_qty_dashboard_temp AS 
select
  raw_data.user_id,
  ru.nickname,
  --rp.name,
  sum(january) as january,
  sum(febuary) as febuary,
  sum(march) as march,
  sum(april) as april,
  sum(may) as may,
  sum(june) as june,
  sum(july) as july,
  sum(august) as august,
  sum(september) as september,
  sum(octorber) as octorber,
  sum(november) as november,
  sum(december) as december,
  round(sum(amount) * 100 / 50000,2) as target50000,
  round(sum(amount) * 100 / 10000,2) as target10000
from
(
select
  user_id,
  case when extract(month from garment_order_date) = 1 then sum(product_uom_qty) else 0 end as january,
  case when extract(month from garment_order_date) = 2 then sum(product_uom_qty) else 0 end as febuary,
  case when extract(month from garment_order_date) = 3 then sum(product_uom_qty) else 0 end as march,
  case when extract(month from garment_order_date) = 4 then sum(product_uom_qty) else 0 end as april,
  case when extract(month from garment_order_date) = 5 then sum(product_uom_qty) else 0 end as may,
  case when extract(month from garment_order_date) = 6 then sum(product_uom_qty) else 0 end as june,
  case when extract(month from garment_order_date) = 7 then sum(product_uom_qty) else 0 end as july,
  case when extract(month from garment_order_date) = 8 then sum(product_uom_qty) else 0 end as august,
  case when extract(month from garment_order_date) = 9 then sum(product_uom_qty) else 0 end as september,
  case when extract(month from garment_order_date) = 10 then sum(product_uom_qty) else 0 end as octorber,
  case when extract(month from garment_order_date) = 11 then sum(product_uom_qty) else 0 end as november,
  case when extract(month from garment_order_date) = 12 then sum(product_uom_qty) else 0 end as december,
  sum(product_uom_qty) as amount
from sale_order so
join sale_order_line sol on sol.order_id = so.id
join product_product pp on pp.id = sol.product_id
join product_template pt on pt.id = pp.product_tmpl_id
where so.state not in ('draft','cancel','cancle')
  and extract(year from garment_order_date) = extract(year from now())
  and pt.categ_id = 19 --POLO
  and so.shop_id = 1   --Only Sale Order
group by
  user_id, garment_order_date
order by 
  user_id) raw_data
left join res_users ru on raw_data.user_id = ru.id
left join res_partner rp on ru.partner_id = rp.id
group by
  raw_data.user_id,
  ru.nickname,
  rp.name
order by
  ru.nickname
        """)
        
class ineco_sale_qty_dashboard(osv.osv):
    _name = 'ineco.sale.qty.dashboard'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users','Sale',readonly=True),
        'nickname': fields.char('Nickname',readonly=True),
        'january': fields.integer('January',readonly=True),
        'febuary': fields.integer('Febuary',readonly=True),
        'march': fields.integer('March',readonly=True),
        'april': fields.integer('April',readonly=True),
        'may': fields.integer('May',readonly=True),
        'june': fields.integer('June',readonly=True),
        'july': fields.integer('July',readonly=True),
        'august': fields.integer('August',readonly=True),
        'september': fields.integer('September',readonly=True),
        'octorber': fields.integer('Octorber',readonly=True),
        'november': fields.integer('November',readonly=True),
        'december': fields.integer('December',readonly=True),
        'target50000': fields.float('% Target 50k', digits=(10,2), readonly=True),
        'target10000': fields.integer('% Target 10k', digits=(10,2), readonly=True),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_dashboard')
        cr.execute(""" CREATE VIEW ineco_sale_qty_dashboard AS 
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_qty_dashboard_temp from ineco_sale_qty_dashboard_temp
                            ) as a
                    ) b
                ) c
        """)

class ineco_color_of_lastyear(osv.osv):
    _name = 'ineco.color.of.lastyear'
    _auto = False
    _columns = {
        'name': fields.char('Color'),
        'total': fields.integer('Total'),
        'm01': fields.integer('January'),
        'm02': fields.integer('February'),
        'm03': fields.integer('March'),
        'm04': fields.integer('April'),
        'm05': fields.integer('May'),
        'm06': fields.integer('June'),
        'm07': fields.integer('July'),
        'm08': fields.integer('August'),
        'm09': fields.integer('September'),
        'm10': fields.integer('Octorber'),
        'm11': fields.integer('November'),
        'm12': fields.integer('December'),        
    }
    _order = 'total desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_color_of_lastyear')
        cr.execute(""" CREATE VIEW ineco_color_of_lastyear AS 
select 
  sc.id,
  sc.name,
  round(sum(sol.product_uom_qty)) as total,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 1 then sol.product_uom_qty else null end),0)) as M01,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 2 then sol.product_uom_qty else null end),0)) as M02,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 3 then sol.product_uom_qty else null end),0)) as M03,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 4 then sol.product_uom_qty else null end),0)) as M04,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 5 then sol.product_uom_qty else null end),0)) as M05,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 6 then sol.product_uom_qty else null end),0)) as M06,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 7 then sol.product_uom_qty else null end),0)) as M07,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 8 then sol.product_uom_qty else null end),0)) as M08,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 9 then sol.product_uom_qty else null end),0)) as M09,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 10 then sol.product_uom_qty else null end),0)) as M10,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 11 then sol.product_uom_qty else null end),0)) as M11,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 12 then sol.product_uom_qty else null end),0)) as M12
from 
  sale_color sc
   join sale_line_property_other slpo on slpo.color_id = sc.id
   join sale_order_line sol on sol.id = slpo.sale_line_id
   join sale_order so on so.id = sol.order_id
where
  extract(year from so.garment_order_date) = extract(year from current_date) - 1
group by
  sc.id,
  sc.name
order by
  sum(sol.product_uom_qty) desc,
  sc.name
limit 10
        """)

class ineco_color_of_year(osv.osv):
    _name = 'ineco.color.of.year'
    _auto = False
    _columns = {
        'name': fields.char('Color'),
        'total': fields.integer('Total'),
        'm01': fields.integer('January'),
        'm02': fields.integer('February'),
        'm03': fields.integer('March'),
        'm04': fields.integer('April'),
        'm05': fields.integer('May'),
        'm06': fields.integer('June'),
        'm07': fields.integer('July'),
        'm08': fields.integer('August'),
        'm09': fields.integer('September'),
        'm10': fields.integer('Octorber'),
        'm11': fields.integer('November'),
        'm12': fields.integer('December'),        
    }
    _order = 'total desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_color_of_year')
        cr.execute(""" CREATE VIEW ineco_color_of_year AS 
select 
  sc.id,
  sc.name,
  round(sum(sol.product_uom_qty)) as total,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 1 then sol.product_uom_qty else null end),0)) as M01,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 2 then sol.product_uom_qty else null end),0)) as M02,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 3 then sol.product_uom_qty else null end),0)) as M03,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 4 then sol.product_uom_qty else null end),0)) as M04,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 5 then sol.product_uom_qty else null end),0)) as M05,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 6 then sol.product_uom_qty else null end),0)) as M06,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 7 then sol.product_uom_qty else null end),0)) as M07,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 8 then sol.product_uom_qty else null end),0)) as M08,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 9 then sol.product_uom_qty else null end),0)) as M09,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 10 then sol.product_uom_qty else null end),0)) as M10,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 11 then sol.product_uom_qty else null end),0)) as M11,
  coalesce(round(sum(case when extract(month from so.garment_order_date) = 12 then sol.product_uom_qty else null end),0)) as M12
from 
  sale_color sc
   join sale_line_property_other slpo on slpo.color_id = sc.id
   join sale_order_line sol on sol.id = slpo.sale_line_id
   join sale_order so on so.id = sol.order_id
where
  extract(year from so.garment_order_date) = extract(year from current_date)
group by
  sc.id,
  sc.name
order by
  sum(sol.product_uom_qty) desc,
  sc.name
limit 10
        """)
