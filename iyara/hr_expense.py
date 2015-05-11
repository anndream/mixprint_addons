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

import time

from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class hr_expense_expense(osv.osv):

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if not default: default = {}
        default.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'hr.expense.expense'),})
        return super(hr_expense_expense, self).copy(cr, uid, id, default, context=context)

    _inherit = "hr.expense.expense"
    _description = "Seq Expense"
    _columns = {
        'description': fields.char('Description', size=256,),
        }

    _defaults = {
            'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr.expense.expense'),                 
            }   

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Order Reference must be unique per Company!'),
    ]
    _order = 'name desc'
    
hr_expense_expense()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
