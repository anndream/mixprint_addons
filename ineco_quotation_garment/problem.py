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
import openerp.addons.decimal_precision as dp
#from openerp import SUPERUSER_ID
#import re
#import tools
#from tools.translate import _
#import logging
#import pooler
#import pytz
#from lxml import etree

class ineco_problem_type(osv.osv):
    _name = 'ineco.problem.type'
    _description = 'Type of Problem'
    _columns = {
        'name': fields.char('Description', size=254,required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]
    _order = 'name'

class ineco_problem(osv.osv):
    
    def _check_cost(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if data.cost <= 0:
                return False
        return True
    
    _name = 'ineco.problem'
    _inherit = ['mail.thread']    
    _description = "Daily Problem"
    _columns = {
        'name': fields.char('Problem No', size=32, required=True,),
        'date': fields.date('Date',required=True),
        'sale_order_id': fields.many2one('sale.order','Sale Order'),
        'target_user_id': fields.many2one('hr.employee','Responsible', required=True),
        'supervisor_user_id': fields.many2one('hr.employee','Supervisor', required=True),
        'manager_user_id': fields.many2one('hr.employee','Manager', required=True),
        'department_id': fields.many2one('hr.department','Department', required=True),
        'type_id': fields.many2one('ineco.problem.type','Type', required=True),
        'note': fields.text('Note', required=True),
        'partner_id': fields.related('sale_order_id', 'partner_id', type='many2one', relation="res.partner", string='Customer', readonly=True),
        'line_ids': fields.related('sale_order_id','order_line',type='one2many', relation="sale.order.line", string="Order Line", readonly=True),
        'cost': fields.float('Cost', digits_compute= dp.get_precision('Account'), required=True),
        'level': fields.selection([
            ('1','1'),
            ('2','2'),
            ('3','3'),
            ('4','4')
            ],'Level', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('pending','Pending'),
            ('approve','Approved'),
            ('cancel','Cancelled')
            ],'Status', select=True, readonly=True),
    }
    _defaults = {
        'name': '/',
        'state': 'draft',
        'date': fields.date.context_today,
    }
    _constraints = [(_check_cost, 'Error: Cost <= 0', ['cost'])]

    def on_change_user_id(self, cr, uid, ids, user_id, context=None):
        if context is None:
            context = {}
        if user_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, user_id)
            if employee  and employee.parent_id:
                manager = self.pool.get('hr.employee').browse(cr, uid, employee.parent_id.id)
                if manager and manager.parent_id:
                    return {'value': {'supervisor_user_id': employee.parent_id.id, 'manager_user_id': manager.parent_id.id}}
                else:
                    return {'value': {'supervisor_user_id': employee.parent_id.id}}
            else:
                return {}
        else:
            return {}

    def on_change_supervisor_id(self, cr, uid, ids, user_id, context=None):
        if context is None:
            context = {}
        if user_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, user_id)
            if employee  and employee.parent_id:
                return {'value': {'manager_user_id': employee.parent_id.id}}
            else:
                return {}
        else:
            return {}
            
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'ineco.problem') or '/'
        return super(ineco_problem, self).create(cr, uid, vals, context=context)

    def button_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'approve'})
        return True

    def button_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def button_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'pending'})
        return True    
    
    def button_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True    