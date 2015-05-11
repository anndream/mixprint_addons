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
from tools.translate import _
#import logging
#import pooler
#import pytz
#from lxml import etree

class res_partner(osv.osv):
    
    def _check_invoiced(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for id in ids:
            sql = """
                select count(*) as total from account_invoice where partner_id = %s and state not in ('cancel','draft')            
            """
            cr.execute(sql % id)
            res2 = cr.dictfetchone()     
            res[id] = res2['total'] > 0
        return res    
    
    _inherit = 'res.partner'
    _columns = {
        'invoice_lock': fields.function(_check_invoiced, type="boolean", string='Invoice Locked',),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, long) or isinstance(ids, int) :
            ids = [ids]
        group_id = self.pool.get('res.groups').search(cr, uid, [('name','=','Full Change Partner')])
        for id in ids:
            data = self.browse(cr, uid, id, context=context)
            user = self.pool.get('res.users').browse(cr, uid, uid)
            full_change = False
            for group in user.groups_id:
                if group.id == group_id[0] and full_change == False:
                    full_change = True
            if data.invoice_lock and not full_change:
                if vals.get('stage_id',False) or vals.get('street',False) or vals.get('street2',False) or vals.get('zip',False) or vals.get('name',False):
                    raise osv.except_osv(_('Error!'), _("Please cancel all invoice when you edit this record.")) 
        return super(res_partner,self).write(cr, uid, ids, vals, context)    