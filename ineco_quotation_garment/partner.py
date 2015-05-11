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
#from openerp import SUPERUSER_ID
#import re
#import tools
#from tools.translate import _
#import logging
#import pooler
#import pytz
#from lxml import etree

class res_partner(osv.osv):
    
    def _get_account_comment(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for data in self.browse(cr, uid, ids):
            result[data.id] = data.account_comment or False
        return result
    
    _inherit = "res.partner"
    _columns = {
        'account_comment': fields.text('Account Information'),     
        'review': fields.function(_get_account_comment, type='boolean', string='Review'),
        'grade_by_volumne': fields.selection([('a','A'),('b','B'),('c','C'),('d','D')], 'Grade by Quantity' 
            ),
        'grade_by_price': fields.selection([('a','A'),('b','B'),('c','C'),('d','D')], 'Grade by Price'
            ),
        'is_user': fields.boolean('Is User'),
        'total_employee': fields.integer('Employee Totals'),
    }
    
    _defaults = {
        'is_user': False,
        'total_employee': 0.0,
    }
