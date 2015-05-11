# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD,. PART. (<http://www.ineco.co.th>).
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

#from datetime import datetime
#from dateutil.relativedelta import relativedelta

import time
from openerp.osv import fields, osv
#import openerp.addons.decimal_precision as dp

class ineco_cheque(osv.osv):

    def _get_day(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'day_month': False
            }
            if obj.cheque_date:          
                result[obj.id]['day_month'] = "%02d" % time.strptime(obj.cheque_date,'%Y-%m-%d').tm_mday         
        return result
    
    _inherit = "ineco.cheque"
    _columns = {
        'day_month': fields.function(_get_day, string="Day", type="char", size=2, multi="_day", 
                store={
                    'ineco.cheque': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                }),
    }
