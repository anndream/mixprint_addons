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

from openerp.osv import fields,osv
from openerp import tools

class ineco_dashboard_story(osv.osv):
    _name = "ineco.dashboard.story"
    _columns = {
        'name': fields.char('Report Path', size=128, required=True),
        'server': fields.char('Jasper Server', size=32, required=True),
        'port': fields.char('Port', size=5,required=True),
        'username': fields.char('Jasper User Name', size=32, required=True),
        'password': fields.char('Jasper Password', size=32, required=True),
        'type': fields.selection([('seq1','Type 1'),('seq2','Type 2')],'Report Type', required=True)
    }

class ineco_crm_dashboard_1(osv.osv):
    """ Ineco CRM Dashboard """
    _name = "ineco.crm.dashboard1"
    _auto = False
    _description = "Ineco CRM Dashboard1 month"
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_crm_dashboard_1')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_crm_dashboard_1 AS (
                select
                  date_part('day', cl.create_date) as day,
                  date_part('month', cl.create_date) as month,
                  date_part('year', cl.create_date) as year,
                  rp_ru.id as saleman_id,
                  sum(cl.planned_revenue) as planned_revenue,
                  cl.state
                from crm_lead cl
                left join res_users ru on cl.user_id = ru.id
                left join res_partner rp_ru on ru.id = rp_ru.id
                where date_part('month', cl.create_date) = date_part('month', now())
                group by
                  EXTRACT(day FROM cl.create_date),
                  EXTRACT(MONTH FROM cl.create_date),
                  EXTRACT(year FROM cl.create_date),
                  rp_ru.id,
                  cl.state
                order by
                  rp_ru.id,
                  date_part('year', cl.create_date),
                  date_part('month', cl.create_date),
                  date_part('day', cl.create_date),
                  cl.state
            )""")
ineco_crm_dashboard_1()

class ineco_crm_dashboard_2(osv.osv):
    """ Ineco CRM Dashboard """
    _name = "ineco.crm.dashboard2"
    _auto = False
    _description = "Ineco CRM Dashboard1 year"
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_crm_dashboard_2')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_crm_dashboard_2 AS (
                select
                  date_part('day', cl.date_deadline) as day,
                  date_part('month', cl.date_deadline) as month,
                  date_part('year', cl.date_deadline) as year,
                  rp_ru.id as saleman_id,
                  ccs.id as stage_id,
                  sum(cl.planned_revenue) as planned_revenue,
                  cl.state
                from crm_lead cl
                left join res_users ru on cl.user_id = ru.id
                left join res_partner rp_ru on ru.id = rp_ru.id
                left join crm_case_stage ccs on cl.stage_id = ccs.id
                where date_part('year', cl.date_deadline) = date_part('year', now())
                and ccs.id = 6
                group by
                  EXTRACT(day FROM cl.date_deadline),
                  EXTRACT(MONTH FROM cl.date_deadline),
                  EXTRACT(year FROM cl.date_deadline),
                  rp_ru.id,
                  ccs.id,
                  cl.state
                order by
                  rp_ru.id,
                  ccs.id,
                  date_part('year', cl.date_deadline),
                  date_part('month', cl.date_deadline),
                  date_part('day', cl.date_deadline),
                  cl.state
            )""")
ineco_crm_dashboard_2()

class ineco_crm_dashboard(osv.osv):
    """ Ineco CRM Dashboard """
    _name = "ineco.crm.dashboard"
    _auto = False
    _description = "Ineco CRM Dashboard"

    _columns = {
        
        'day': fields.char('day', size=10, readonly=True, help="day"),
        'month': fields.char('month', size=10, readonly=True, help="month"),
        'year': fields.char('year', size=10, readonly=True, help="year"),
        'saleman_id':fields.many2one('res.users', 'Saleman', readonly=True),
        'planned_revenue': fields.float('Planned Revenue',digits=(16,2),readonly=True),
        'state': fields.char('State', size=10, readonly=True, help="State"),
    }
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_crm_dashboard')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_crm_dashboard AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_crm_dashboard_1 from ineco_crm_dashboard_1

                            ) as a
                    ) b
                ) c
            )""")

ineco_crm_dashboard()

class ineco_crm_dashboard_year(osv.osv):
    """ Ineco CRM Dashboard """
    _name = "ineco.crm.dashboard.year"
    _auto = False
    _description = "Ineco CRM Dashboard "

    _columns = {
        
        'day': fields.char('day', size=10, readonly=True, help="day"),
        'month': fields.char('month', size=10, readonly=True, help="month"),
        'year': fields.char('year', size=10, readonly=True, help="year"),
        'saleman_id':fields.many2one('res.users', 'Saleman', readonly=True),
        'stage_id':fields.many2one('res.users', 'Stage', readonly=True),
        'planned_revenue': fields.float('Planned Revenue',digits=(16,2),readonly=True),
        'state': fields.char('State', size=10, readonly=True, help="State"),
    }
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_crm_dashboard_year')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_crm_dashboard_year AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_crm_dashboard_2 from ineco_crm_dashboard_2

                            ) as a
                    ) b
                ) c
            )""")

ineco_crm_dashboard_year()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
