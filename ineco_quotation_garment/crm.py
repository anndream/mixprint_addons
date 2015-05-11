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

# 2013-02-10     POP-001    ADD New notification on sale user
from datetime import datetime, timedelta
from openerp.osv import fields, osv
import time
#import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

class crm_lead(osv.osv):

    _inherit = 'crm.lead'
    _description = "Lock when opps lost"
    _columns = {
        'opportunity_cost_ids': fields.one2many('ineco.opportunity.cost','opportunity_id','Costs'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals.get('stage_id',False):
            crm_obj = self.pool.get('crm.lead').browse(cr, uid, ids)[0]
            if (crm_obj.stage_id.state == 'cancel') and (crm_obj.stage_id.type == 'opportunity'):
                raise osv.except_osv('Unable to change stage!', 'Lost Forever.')
        res = super(crm_lead, self).write(cr, uid, ids, vals, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: