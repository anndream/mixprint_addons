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

from base_status.base_stage import base_stage
import crm
from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import fields, osv
import time
import tools
from tools.translate import _
from tools import html2plaintext

from base.res.res_partner import format_address


class crm_lead(osv.osv):
    
    _description = "Lead/Opportunity"
    _inherit = "crm.lead"

    def create(self, cr, uid, vals, context=None):        
        if 'date_deadline' not in vals:
            date_ref = datetime.now().strftime('%Y-%m-%d')
            next_date = (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=30))            
            vals.update({'date_deadline': next_date.strftime('%Y-%m-%d')})
        return super(crm_lead, self).create(cr, uid, vals, context)
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
