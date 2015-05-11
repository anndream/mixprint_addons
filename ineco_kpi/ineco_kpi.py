# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

import logging
import openerp.pooler
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round
from openerp import SUPERUSER_ID
import openerp.tools

class ineco_kpi_year(osv.osv):
    _name = 'ineco.kpi.year'
    _description = 'Year of KPI'
    _columns = {
        'name': fields.char('Year', size=10, required=True),
    }    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Year must be unique!')
    ]

class ineco_kpi_category(osv.osv):
    _name = 'ineco.kpi.category'
    _description = 'Category of KPI'
    _columns = {
        'name': fields.char('Category', size=10, required=True),
    }    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Category must be unique!')
    ]
    
class ineco_kpi_sale(osv.osv):
    
    def _actual_calc(self, cr, uid, ids, prop, unknow_none, context=None):
        """ Calculates total hours and total no. of cycles for a production order.
        @param prop: Name of field.
        @param unknow_none:
        @return: Dictionary of values.
        """
        result = {}
        for id in ids:
            result[id] = {
                'actual': 0.0,
                'percent': 0.0,
            }
            data = self.browse(cr, uid, [id], context=context)[0]
            order_sql = "select * from sale_order where user_id = %s and state in ('done') and date_order >= '%s' and date_order <= '%s' " % (data.sale_id.id, data.date_start, data.date_end)
            cr.execute(order_sql )
            total = 0
            for field in cr.dictfetchall():
                if data.dimension == 'value':
                    total = total + field['amount_untaxed'] or 0.0
                elif data.dimension == 'quantity':
                    total = total + 1
                else:
                    total = total + 0
            result[id]['actual'] = total
            if total:
                result[id]['percent'] = total * 100 / data.target
            else:
                result[id]['percent'] = 0
        return result
    
    def _get_kpi(self, cr, uid, ids, context=None):
        return ids

    def _get_order(self, cr, uid, ids, context=None):
        tmp_result = []
        for line in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            sale_sql = "select id from ineco_kpi_sale where sale_id = %s and date_start <= '%s' and date_end >= '%s'" % (line.user_id.id, line.date_order, line.date_order )
            cr.execute(sale_sql)
            tmp_result += [(r[0]) for r in cr.fetchall()]
        return tmp_result
    
    _name = 'ineco.kpi.sale'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'KPI for Sale'
    _columns = {
        'name': fields.char('Description', size=254, required=True),
        'year_id': fields.many2one('ineco.kpi.year','Year', required=True),
        'category_id': fields.many2one('ineco.kpi.category','Category', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),
        'sale_id': fields.many2one('res.users','Sale', required=True),
        'team_id': fields.many2one('crm.case.section', 'Sales Team'),
        'dimension': fields.selection([('value', 'Amount'), 
                                       ('quantity', 'Quantity')], 'Dimension', required=True),
        'target': fields.float('Target', digits_compute=dp.get_precision('Account')),
        'actual': fields.function(_actual_calc, type='float', digits_compute=dp.get_precision('Account'), 
                                  string='Actual', 
                                  store={
                                         'ineco.kpi.sale': (_get_kpi, [], 10),
                                         'sale.order': (_get_order, [], 10),}, 
                                  multi="sums"),
        'percent': fields.function(_actual_calc, type='float', digits_compute=dp.get_precision('Account'), 
                                  string='Percent', store={
                                        'ineco.kpi.sale': (_get_kpi, [], 10),
                                        'sale.order': (_get_order, [], 15),}, multi="sums"),
    }
    _defaults = {
        'name': '...',
        'dimension': 'value',
    }
    _sql_constraints = [
        ('year_category_sale_dimension_uniq', 'unique (year_id, category_id, sale_id, dimension)', 'Year and Category must be unique!')
    ]
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True

class ineco_kpi_quotation(osv.osv):
    
    def _actual_calc(self, cr, uid, ids, prop, unknow_none, context=None):
        """ Calculates total hours and total no. of cycles for a production order.
        @param prop: Name of field.
        @param unknow_none:
        @return: Dictionary of values.
        """
        result = {}
        for id in ids:
            result[id] = {
                'actual': 0.0,
                'percent': 0.0,
            }
            data = self.browse(cr, uid, [id], context=context)[0]
            order_sql = "select * from sale_order where user_id = %s and state not in ('cancel') and date_order >= '%s' and date_order <= '%s' " % (data.sale_id.id, data.date_start, data.date_end)
            cr.execute(order_sql )
            total = 0
            for field in cr.dictfetchall():
                if data.dimension == 'value':
                    total = total + field['amount_untaxed'] or 0.0
                elif data.dimension == 'quantity':
                    total = total + 1
                else:
                    total = total + 0
            result[id]['actual'] = total
            if total:
                result[id]['percent'] = total * 100 / data.target
            else:
                result[id]['percent'] = 0
        return result
    
    def _get_kpi(self, cr, uid, ids, context=None):
        return ids

    def _get_order(self, cr, uid, ids, context=None):
        tmp_result = []
        for line in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            sale_sql = "select id from ineco_kpi_quotation where sale_id = %s and date_start <= '%s' and date_end >= '%s'" % (line.user_id.id, line.date_order, line.date_order )
            cr.execute(sale_sql)
            tmp_result += [(r[0]) for r in cr.fetchall()]
        return tmp_result
    
    _name = 'ineco.kpi.quotation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'KPI for Sale'
    _columns = {
        'name': fields.char('Description', size=254, required=True),
        'year_id': fields.many2one('ineco.kpi.year','Year', required=True),
        'category_id': fields.many2one('ineco.kpi.category','Category', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),
        'sale_id': fields.many2one('res.users','Sale', required=True),
        'team_id': fields.many2one('crm.case.section', 'Sales Team'),
        'dimension': fields.selection([('value', 'Amount'), 
                                       ('quantity', 'Quantity')], 'Dimension', required=True),
        'target': fields.float('Target', digits_compute=dp.get_precision('Account')),
        'actual': fields.function(_actual_calc, type='float', digits_compute=dp.get_precision('Account'), 
                                  string='Actual', 
                                  store={
                                         'ineco.kpi.quotation': (_get_kpi, [], 10),
                                         'sale.order': (_get_order, [], 10),}, 
                                  multi="sums"),
        'percent': fields.function(_actual_calc, type='float', digits_compute=dp.get_precision('Account'), 
                                  string='Percent', store={
                                         'ineco.kpi.quotation': (_get_kpi, [], 10),
                                         'sale.order': (_get_order, [], 15),}, multi="sums"),
    }
    _defaults = {
        'name': '...',
        'dimension': 'value',
    }
    _sql_constraints = [
        ('year_category_sale_dimension_uniq', 'unique (year_id, category_id, sale_id, dimension)', 'Year and Category must be unique!')
    ]
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True

class ineco_kpi_opportunity(osv.osv):
    
    def _actual_calc(self, cr, uid, ids, prop, unknow_none, context=None):
        """ Calculates total hours and total no. of cycles for a production order.
        @param prop: Name of field.
        @param unknow_none:
        @return: Dictionary of values.
        """
        result = {}
        for id in ids:
            result[id] = {
                'actual': 0.0,
                'percent': 0.0,
            }
            data = self.browse(cr, uid, [id], context=context)[0]
            order_sql = "select * from crm_lead where type = 'opportunity' and state not in ('draft','cancel') and user_id = %s and date_deadline >= '%s' and date_deadline <= '%s' " % (data.sale_id.id, data.date_start, data.date_end)
            cr.execute(order_sql )
            total = 0
            for field in cr.dictfetchall():
                if data.dimension == 'value':
                    total = total + field['planned_revenue'] or 0.0
                elif data.dimension == 'quantity':
                    total = total + 1
                else:
                    total = total + 0
            result[id]['actual'] = total
            if total:
                result[id]['percent'] = total * 100 / data.target
            else:
                result[id]['percent'] = 0
        return result
    
    def _get_kpi(self, cr, uid, ids, context=None):
        return ids

    def _get_order(self, cr, uid, ids, context=None):
        tmp_result = []
        for line in self.pool.get('crm.lead').browse(cr, uid, ids, context=context):
            if line.type == 'opportunity':
                sale_sql = "select id from ineco_kpi_opportunity where sale_id = %s and date_start <= '%s' and date_end >= '%s'" % (line.user_id.id, line.date_deadline, line.date_deadline )
                cr.execute(sale_sql)
                tmp_result += [(r[0]) for r in cr.fetchall()]
        return tmp_result
    
    _name = 'ineco.kpi.opportunity'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'KPI for Sale'
    _columns = {
        'name': fields.char('Description', size=254, required=True),
        'year_id': fields.many2one('ineco.kpi.year','Year', required=True),
        'category_id': fields.many2one('ineco.kpi.category','Category', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date', required=True),
        'sale_id': fields.many2one('res.users','Sale', required=True),
        'team_id': fields.many2one('crm.case.section', 'Sales Team'),
        'dimension': fields.selection([('value', 'Amount'), 
                                       ('quantity', 'Quantity')], 'Dimension', required=True),
        'target': fields.float('Target', digits_compute=dp.get_precision('Account')),
        'actual': fields.function(_actual_calc, type='float', digits_compute=dp.get_precision('Account'), 
                                  string='Actual', 
                                  store={
                                         'ineco.kpi.opportunity': (_get_kpi, [], 10),
                                         'crm.lead': (_get_order, [], 10),}, 
                                  multi="sums"),
        'percent': fields.function(_actual_calc, type='float', digits_compute=dp.get_precision('Account'), 
                                  string='Percent', store={
                                        'ineco.kpi.opportunity': (_get_kpi, [], 10),
                                        'crm.lead': (_get_order, [], 15),}, multi="sums"),
    }
    _defaults = {
        'name': '...',
        'dimension': 'value',
    }
    _sql_constraints = [
        ('year_category_sale_dimension_uniq', 'unique (year_id, category_id, sale_id, dimension)', 'Year and Category must be unique!')
    ]
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
