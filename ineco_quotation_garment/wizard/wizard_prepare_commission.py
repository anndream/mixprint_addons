# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today INECO., Part., Ltd. (<http://www.ineco.co.th>).
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

from openerp.osv import fields, osv
import time

class ineco_prepare_commission(osv.osv_memory):
    
    _name = 'ineco.prepare.commission'
    _description = 'Wizard prepare commission'
    _columns = {
        'commission_date': fields.date('Commission Date'),
    }
    _defaults = {
        'commission_date': time.strftime('%Y-%m-%d'),
    }
    
    def update_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        if active_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            for invoice in self.pool.get('account.invoice').browse(cr, uid, active_ids):
                if invoice.state == 'paid' and (invoice.commission_ready or invoice.type == 'out_refund') :
                    commission_rate = invoice.user_id.commission_rate or 0.0 / 100
                    invoice_amount = invoice.amount_untaxed or 0.00
                    commission = invoice_amount * commission_rate
                    invoice.write({'commission_sale': commission,'commission_date': data['commission_date'] })
            
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
