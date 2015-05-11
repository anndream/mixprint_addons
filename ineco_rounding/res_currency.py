# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import re
import time

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_round, float_is_zero, float_compare
from openerp.tools.translate import _

CURRENCY_DISPLAY_PATTERN = re.compile(r'(\w+)\s*(?:\((.*)\))?')

class res_currency(osv.osv):
    
    _inherit = 'res.currency'
    
    def round(self, cr, uid, currency, amount):
        sql = """
            select 
              round(%s,
              case 
                when position('1' in rounding::varchar) - position('.' in rounding::varchar) <= 0 then 0
                else  position('1' in rounding::varchar) - position('.' in rounding::varchar)
              end) as amount
            from 
              res_currency
            where id = %s        
        """
        cr.execute(sql % (amount, currency.id))
        datas = cr.dictfetchall()
        return datas[0]['amount'] or amount
        #return float_round(amount, precision_rounding=currency.rounding)
    