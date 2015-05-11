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
from datetime import datetime

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    _description = 'Status Analytic Account'
    _columns = {
        'quotation_id': fields.many2one('sale.order', '1. Quotation'),
        'quotation_date': fields.related('quotation_id', 'date_sale_order', type='date', string='Quotation Date'),                
        'sale_order_id': fields.many2one('sale.order', '2. Sale Order'),
        'sale_order_date': fields.related('sale_order_id', 'date_sale_order', type='date', string='Sale Order Date'),                        
        'po_customer': fields.char('3. PO Customer', size=64),      
        'po_customer_date':fields.date('PO Customer Date'),        
        'purchase_order_id' :fields.many2one('purchase.order', '4. Purchase Order'),
        'purchase_order_date': fields.related('purchase_order_id', 'date_order', type='date', string='Purchase Order Date'),                        
        'open_lc_tt': fields.selection([ ('tt','T/T'),('cif','CIF'),('fob','FOB'),('exw','EXW')],'5. Open L/C OR T/T'),
        'opne_lc_tt_bank':fields.char('Open L/C OR T/T Bank', size=256), 
        'opne_lc_tt_no':fields.char('Open L/C OR T/T No.',  size=64), 
        'opne_lc_tt_date':fields.date('Open L/C OR T/T Date'),                                   
        'ex_wh': fields.selection([('ex_china','Ex-Warehouse China'),('ex_singapore','Ex-Warehouse Singapore')],'6. EX-Warehouse'),                          
        'ex_wh_date':fields.date('EX-Warehouse Date'), 
        'etd_date':fields.date('7. ETD Date'),  
        'eta_date':fields.date('8. ETA Date'),
        'to_wh_iyara_date':fields.date('9. To Warehouse Iyara Date'),
        'test_load_date':fields.date('10. Test Load at Warehouse Iyara /at Site'),
        'send_to_site_date':fields.date('11. Send To Site Date'),
        'finished_install_date':fields.date('12. Finished Installation Date'),
        'comm_system_date':fields.date('13. Commissioning System Date'),        
        'training_date':fields.date('14. Training Date'),        
        'start_warranty_date':fields.date('15. Start Warranty Date'),  
        'end_warranty_date':fields.date('16. End Warranty Date'),                                              
        'invoice_down_payment': fields.many2one('account.invoice', 'Down Payment.'),
        'invoice_two_payment': fields.many2one('account.invoice', '2 Payment.'),
        'invoice_three_payment': fields.many2one('account.invoice', '3 Payment.'),
        'invoice_four_payment': fields.many2one('account.invoice', '4 Payment.'),
        'date_down_payment':  fields.related('invoice_down_payment',  'date_invoice', type='date', string='Down Payment Date'),
        'date_two_payment':   fields.related('invoice_two_payment',   'date_invoice', type='date', string='2 Payment Date'),
        'date_three_payment': fields.related('invoice_three_payment', 'date_invoice', type='date', string='3 Payment Date'),
        'date_four_payment': fields.related('invoice_four_payment', 'date_invoice', type='date', string='4 Payment Date'),        
        'iyara_description': fields.text('Description'),
        'end_project': fields.boolean('End Project'),
        'partner_use_id': fields.many2one('res.partner', 'Customer Use'),
    
    }
    _defaults = {
        'end_project': False,
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' ' + name
            res.append((record['id'], name))
        return res
            
account_analytic_account()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
