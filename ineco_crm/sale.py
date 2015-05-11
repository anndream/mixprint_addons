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

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
#import time
#from openerp import pooler
from openerp.osv import fields, osv
#from openerp.tools.translate import _
#from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import openerp.addons.decimal_precision as dp
#from openerp import netsvc

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'sale_team_id': fields.many2one('crm.case.section', 'Sale Team'),
        'lead_id': fields.many2one('crm.lead', 'Lead/Opportunity'),
    }
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        #if the chosen partner is not a company and has a parent company, use the parent to choose the delivery, the 
        #invoicing addresses and all the fields related to the partner.
        if part.parent_id and not part.is_company:
            part = part.parent_id
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        dedicated_saleteam = (part.sale_team_id and part.sale_team_id.id) or (user.default_section_id and  user.default_section_id.id)
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
            'section_id': dedicated_saleteam or False,
            'sale_team_id': dedicated_saleteam or False,
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: