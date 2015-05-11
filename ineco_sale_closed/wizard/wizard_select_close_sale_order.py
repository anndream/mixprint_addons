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

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

class wizard_select_close_saleorder(osv.osv_memory):
    
    _name = 'wizard.select.close.saleorder'
    _description = 'Select Sale order to Close sale'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'partner_ids': fields.many2many('res.partner', 'closesale_partner_rel', 'wizard_id', 'partner_id', 'Customer(s)', readonly="1"),
        'invoice_ids': fields.many2many('account.invoice', 'closesale_invoice_rel', 'wizard_id', 'invoice_id', 'Invoice (s)'),
    }

    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context={}
        res = super(wizard_select_close_saleorder, self).default_get(cr, uid, fields_list, context=context)
        if context.get('active_ids', False) :
            invoice_obj = self.pool.get('account.invoice').browse(cr, uid, context.get('active_ids'))[0]
            child_ids = self.pool.get('res.partner').search(cr, uid, [('parent_id','child_of',invoice_obj.partner_id.id)])
            if not invoice_obj.partner_id.id:
                child_ids.append(invoice_obj.partner_id.id)
            invoice_draft_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id','in',child_ids)])
            invoice_ids = []
            for invoice in self.pool.get('account.invoice').browse(cr, uid, invoice_draft_ids):
                if not invoice.close_sale_no and invoice.state == 'paid' :
                    invoice_ids.append(invoice.id)
                res = {
                     'partner_id': invoice_obj.partner_id.id, 
                     'partner_ids': [(6, 0, child_ids)],
                     'invoice_ids': [(6, 0, invoice_ids)]
                }
        return res
    
    def close_sale(self, cr, uid, ids, context=None):        
        data = self.read(cr, uid, ids, [], context=context)[0]
        if data:
            sale_ids = []
            for invoice in self.pool.get('account.invoice').browse(cr, uid, data['invoice_ids']):
                if invoice.origin:
                    sale_no_list = invoice.origin.split(':')
                    sale_order_ids = self.pool.get('sale.order').search(cr, uid, [('name','in',sale_no_list),('sale_close_no','=',False)])
                    for id in sale_order_ids:
                        sale_ids.append(id)
                    #Add Commission Line
                    commission_rate = invoice.user_id.commission_rate / 100
                    invoice_amount = invoice.amount_untaxed or 0.00
                    commission = invoice_amount * commission_rate
                    invoice.write({'commission_sale': commission,'commission_date': time.strftime('%Y-%m-%d') })

            if sale_ids:
                #print sale_ids
                next_no = self.pool.get('ir.sequence').get(cr, uid, 'ineco.sale.close') or False
                self.pool.get('sale.order').write(cr, uid, sale_ids, {'sale_close_no': next_no})
        return True

wizard_select_close_saleorder()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: