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

#import time
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
#from operator import itemgetter

#import logging
#import openerp.pooler
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
#from openerp.tools.translate import _
#from openerp.tools.float_utils import float_round
#from openerp import SUPERUSER_ID
#import openerp.tools

class inece_kpi_create_opportunity(osv.osv_memory):
    
    _name = "ineco.kpi.create_opportunity"
    _columns = {
        'year_id': fields.many2one('ineco.kpi.year','Year',required=True),
        'category_id': fields.many2one('ineco.kpi.category','Category',required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_finish': fields.date('Finish Date', required=True),
        'dimension': fields.selection([('value', 'Amount'), 
                                       ('quantity', 'Quantity')], 'Dimension', required=True),
        'target': fields.float('Target', digits_compute=dp.get_precision('Account')),
    }

    def create_wizard(self, cr, uid, ids, context=None):
        
        data = self.read(cr, uid, ids)[0]
        sale_user_ids = self.pool.get('res.users').search(cr, uid, [('default_section_id','!=',False)])
        for sale_id in sale_user_ids:
            data_ids = self.pool.get('ineco.kpi.opportunity').search(cr, uid, 
                    [('year_id', '=', data['year_id'][0]), 
                     ('category_id','=',data['category_id'][0]),
                     ('sale_id','=',sale_id) 
                    ])
            if not data_ids:
                new_data = {
                    'name':'...',
                    'year_id': data['year_id'][0],
                    'category_id': data['category_id'][0],
                    'sale_id': sale_id,
                    'dimension': data['dimension'],
                    'target': data['target'],
                    'date_start': data['date_start'],
                    'date_end': data['date_finish'],
                }
                self.pool.get('ineco.kpi.opportunity').create(cr, uid, new_data)
                
        return {'type':'ir.actions.act_window_close' }
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: