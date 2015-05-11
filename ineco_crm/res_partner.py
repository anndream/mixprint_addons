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

# 2013-03-01    POP-001    Add Nickname

from openerp.osv import fields, osv
import time
from datetime import datetime

class res_partner(osv.osv):
    
    _inherit = 'res.partner'
    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'refresh_count': 0,
    }

    def schedule_refresh(self, cr, uid, context={}):
        #print 'Refresh Partner Start'
        partner_ids = self.pool.get('res.partner').search(cr, uid, [])
        for partner_id in partner_ids:
            #partner = self.pool.get('res.partner').browse(cr, uid, [partner_id])[0]
            cr.execute("""
                update res_partner
                set last_lead_count = 
                  (
                    select 
                      date_part('day', now() - max(create_date))
                    from 
                      crm_lead 
                    where type in ('lead','opportunity') and partner_id is not null
                      and partner_id = res_partner.id
                  )
                where id = %s            
            """  % (partner_id))
            cr.execute("""
                update res_partner
                set last_opportunity_count = 
                  (
                    select 
                      date_part('day', now() - max(create_date))
                    from 
                      crm_lead 
                    where type = 'opportunity' and partner_id is not null
                      and partner_id = res_partner.id
                  )
                where id = %s            
            """  % (partner_id))
            cr.execute("""
                update res_partner
                set last_quotation_count = 
                  (
                    select 
                      date_part('day', now() - max(create_date))
                    from 
                      sale_order 
                    where state not in ('cancel')
                      and partner_id = res_partner.id
                  )
                where id = %s            
            """  % (partner_id))
            cr.execute("""
                update res_partner
                set last_saleorder_count = 
                  (
                    select 
                      date_part('day', now() - max(create_date))
                    from 
                      sale_order 
                    where state in ('done')
                      and partner_id = res_partner.id
                  )
                where id = %s            
            """  % (partner_id))
            cr.execute("""
                update res_partner
                set last_phonecall = (select max(last_phonecall) from res_partner rp2 where rp2.parent_id = res_partner.id and rp2.last_phonecall is not null)
                where 
                   id = %s
                   and parent_id is null        
            """ % (partner_id))
            #count = partner.refresh_count or 0.0 + 1
            #partner.write({'refresh_count': count})
            #print partner_id
        cr.execute("""
            update res_partner
                set last_lead_count = date_part('day', now() - '2012-01-01 00:00:00')       
            where id not in (select distinct partner_id from crm_lead where type in ('lead','opportunity') and partner_id is not null)                
        """ )
        cr.execute("""
            update res_partner
                set last_opportunity_count = date_part('day', now() - '2012-01-01 00:00:00')       
            where id not in (select distinct partner_id from crm_lead where type in ('opportunity') and partner_id is not null)                
        """)
        cr.execute("""
            update res_partner
                set last_quotation_count = date_part('day', now() - '2012-01-01 00:00:00')       
            where id not in (select distinct partner_id from sale_order where state not in ('cancel'))                
        """)
        cr.execute("""
            update res_partner
                set last_saleorder_count = date_part('day', now() - '2012-01-01 00:00:00')       
            where id not in (select distinct partner_id from sale_order where state in ('done'))                
        """ )
        cr.execute("""
            update
              res_partner
            set
              last_phonecall = b.last_update
            from 
                (select
                  a.id,
                  greatest(a.last_phonecall, a.lead_create, a.lead_update)::timestamp(0) as last_update
                from
                    (select 
                      res_partner.id,
                      last_phonecall,
                      (select max(create_date) from crm_lead
                       where partner_id = res_partner.id) as lead_create,
                      (select max(write_date) from crm_lead
                       where partner_id = res_partner.id) as lead_update  
                    from res_partner) as a) as b
            where
              b.id = res_partner.id        
        """)
        cr.execute("""
            update res_partner
            set last_date_count = date_part('day',now() - last_phonecall)
        """)
        cr.execute("""
            update res_partner
            set last_date_count = 366 + date_part('day', now() - '2013-01-01 00:00:00')
            where last_phonecall is null
        """)
        cr.execute("""
            update crm_lead
            set last_date_count = date_part('day',now() - create_date)
            where state not in ('cancel','done')        
        """
        )
        #print 'Finish'
    
    standard_date_count = 365

    def _opportunity_meeting_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,{'opportunity_count': 0, 'meeting_count': 0,'phonecall_count':0}), ids))
        # the user may not have access rights for opportunities or meetings
        try:
            for partner in self.browse(cr, uid, ids, context):
                child_opportunity_count = 0
                child_meeting_count = 0
                child_phonecall_count = 0
                for child in partner.child_ids:
                    child_opportunity_count += len(child.opportunity_ids)
                    child_meeting_count += len(child.meeting_ids)
                    child_phonecall_count += len(child.phonecall_ids)
                res[partner.id] = {
                    'opportunity_count': (len(partner.opportunity_ids) or 0.0) + child_opportunity_count,
                    'meeting_count': (len(partner.meeting_ids) or 0.0) + child_meeting_count,
                    'phonecall_count': (len(partner.phonecall_ids) or 0.0) + child_phonecall_count,
                }
        except:
            pass
        return res
    
    def _last_date_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            sql = """
                select 
                  extract(days from now() - GREATEST(
                  coalesce((select max(create_date) from crm_phonecall where partner_id = rp.id), rp.create_date) ,
                  coalesce((select max(case when write_date is null then create_date else write_date end) from crm_lead where partner_id = rp.id), rp.create_date)))
                from
                  res_partner rp
                where 
                  rp.id = %s
              """
            cr.execute(sql % partner.id)
            last_date_count = cr.fetchone()[0] or 0.0
            #last_date_count = 0
            #if partner.last_phonecall:
            #    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
            #    date_start = datetime.strptime(partner.last_phonecall,'%Y-%m-%d %H:%M:%S')
            #    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
            #    last_date_count += (date_finished-date_start).days 
            res[partner.id] = last_date_count
            #reset main company again
            if partner.parent_id:
                res[partner.parent_id.id] = last_date_count
        return res
    
    def _last_lead_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for id in ids:
            last_date_count = 0
            partner = self.browse(cr, uid, [id], context=context)[0]
            if partner:
                sql = """
                    select to_char(max(create_date), 'yyyy-mm-dd HH:MM:SS') as lead_last_date 
                    from crm_lead where type in ('lead', 'opportunity') and partner_id = %s
                """
                cr.execute(sql % id)
                res2 = cr.dictfetchone()
                if res2 and res2['lead_last_date'] :
                    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    date_start = datetime.strptime(res2['lead_last_date'],'%Y-%m-%d %H:%M:%S')
                    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                    last_date_count += (date_finished-date_start).days 
                    res[id] = last_date_count
                    #reset main company again
                    if partner.parent_id:
                        res[partner.parent_id.id] = last_date_count
                else:
                    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    date_start = datetime.strptime('2013-01-01','%Y-%m-%d')
                    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                    last_date_count += (date_finished-date_start).days 
                    res[id] = self.standard_date_count + last_date_count
                    #reset main company again
                    if partner.parent_id:
                        res[partner.parent_id.id] = last_date_count
        return res

    def _last_opportunity_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for id in ids:
            last_date_count = 0
            partner = self.browse(cr, uid, [id], context=context)[0]
            if partner:
                sql = """
                    select to_char(max(create_date), 'yyyy-mm-dd HH:MM:SS') as lead_last_date 
                    from crm_lead where type in ('opportunity') and partner_id = %s
                """
                cr.execute(sql % id)
                res2 = cr.dictfetchone()
                if res2 and res2['lead_last_date'] :
                    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    date_start = datetime.strptime(res2['lead_last_date'],'%Y-%m-%d %H:%M:%S')
                    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                    last_date_count += (date_finished-date_start).days 
                    res[id] = last_date_count
                    if partner.parent_id:
                        res[partner.parent_id.id] = last_date_count
                else:
                    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    date_start = datetime.strptime('2013-01-01','%Y-%m-%d')
                    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                    last_date_count += (date_finished-date_start).days 
                    res[id] = self.standard_date_count + last_date_count
                    if partner.parent_id:
                        res[partner.parent_id.id] = last_date_count
        return res

    def _last_quotation_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for id in ids:
            last_date_count = 0
            partner = self.browse(cr, uid, [id], context=context)[0]
            if partner:
                sql = """
                    select to_char(max(create_date), 'yyyy-mm-dd HH:MM:SS') as lead_last_date 
                    from sale_order where state not in ('done','cancel') and partner_id = %s
                """
                cr.execute(sql % id)
                res2 = cr.dictfetchone()
                if res2 and res2['lead_last_date'] :
                    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    date_start = datetime.strptime(res2['lead_last_date'],'%Y-%m-%d %H:%M:%S')
                    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                    last_date_count += (date_finished-date_start).days 
                    res[id] = last_date_count
                    if partner.parent_id:
                        res[partner.parent_id.id] = last_date_count
                else:
                    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    date_start = datetime.strptime('2013-01-01','%Y-%m-%d')
                    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                    last_date_count += (date_finished-date_start).days 
                    res[id] = self.standard_date_count + last_date_count
                    if partner.parent_id:
                        res[partner.parent_id.id] = last_date_count
        return res

    def _last_saleorder_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for id in ids:
            last_date_count = 0
            partner = self.browse(cr, uid, [id], context=context)[0]
            if partner:
                sql = """
                    select to_char(max(date_confirm), 'yyyy-mm-dd HH:MM:SS') as lead_last_date 
                    from sale_order where state in ('done') and partner_id = %s
                """
                cr.execute(sql % id)
                res2 = cr.dictfetchone()
                if res2 and res2['lead_last_date'] :
                    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                    date_start = datetime.strptime(res2['lead_last_date'],'%Y-%m-%d %H:%M:%S')
                    date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                    last_date_count += (date_finished-date_start).days 
                    res[id] = last_date_count
                    if partner.parent_id:
                        res[partner.parent_id.id] = last_date_count
                else:
                    res[id] = 365
        return res

    def _get_ids_from_lead(self, cr, uid, ids, context=None):
        result = []
        for id in ids:
            lead = self.pool.get('crm.lead').browse(cr, uid, [id])[0]
            if lead and lead.partner_id:
                result.append(lead.partner_id.id)
        return result

    def _get_ids_from_saleorder(self, cr, uid, ids, context=None):
        result = []
        for id in ids:
            data = self.pool.get('sale.order').browse(cr, uid, [id])[0]
            if data and data.partner_id:
                result.append(data.partner_id.id)
        return result

    _columns = {
        'last_phonecall': fields.datetime('Last Contact Date'),
        'last_date_count': fields.function(_last_date_count, type="integer", string='Contacted Update',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'crm.lead': (_get_ids_from_lead,[],10),
            }, track_visibility='always'),
        'opportunity_count': fields.function(_opportunity_meeting_count, string="Opportunity", type='integer', multi='opp_meet'),
        'meeting_count': fields.function(_opportunity_meeting_count, string="Meeting", type='integer', multi='opp_meet'),
        'phonecall_count': fields.function(_opportunity_meeting_count, string="Phonecall", type='integer', multi='opp_meet'),
        #POP-001
        'nick_name': fields.char('Nick Name', sieze=64, select=True),
        'last_lead_count': fields.function(_last_lead_count, type="integer", string='Lead Count',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'crm.lead': (_get_ids_from_lead,[],10),
            }, track_visibility='always'),
        'last_opportunity_count': fields.function(_last_opportunity_count, type="integer", string='Opportunity Count',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'crm.lead': (_get_ids_from_lead,[],10),
            }, track_visibility='always'),
        'last_quotation_count': fields.function(_last_quotation_count, type="integer", string='Quotation Count',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order': (_get_ids_from_saleorder,[],10),
            }, track_visibility='always'),
        'last_saleorder_count': fields.function(_last_saleorder_count, type="integer", string='Sale Count',
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order': (_get_ids_from_saleorder,[],10),
            }, track_visibility='always'),
        'refresh_count': fields.integer('Refresh Count'),
        #Add Sale Team
        'sale_team_id': fields.many2one('crm.case.section','Sale Team'),
    }
