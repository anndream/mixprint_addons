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
from openerp.osv import fields, osv
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.translate import _

class sale_make_purchase(osv.osv_memory):
    _name = "sale.make.purchase"
    _description = "Ineco Sale Make Purchase"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Supplier', required=True,domain=[('supplier', '=', True)]),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True,),        
        'date_planned': fields.date('Scheduled Date', required=True),        
    }
    _defaults = {
        'date_planned': fields.date.context_today,
    }
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(sale_make_purchase, self).view_init(cr, uid, fields_list, context=context)
        record_id = context and context.get('active_id', False) or False
        tender = self.pool.get('sale.order').browse(cr, uid, record_id, context=context)
        product_ids = []        
        for line in tender.order_line:
            if line.product_id.sale_make_purchase == True:
                product_ids.append(line.product_id.id)

        if len(product_ids) == 0:
            raise osv.except_osv(_('Error!'), _('No Product Make Purchase.'))
        return res

    def create_order(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        sale_order = self.pool.get('sale.order').browse(cr, uid, record_id, context=context)
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        new_ids = []                     
        for make in self.browse(cr, uid, ids, context=context):
            supplier = res_partner.browse(cr, uid, make.partner_id.id, context=context)
            supplier_pricelist = supplier.property_product_pricelist_purchase or False
            location_id = make.warehouse_id.lot_input_id.id            
            purchase_id = purchase_order.create(cr, uid, {
                        'origin': sale_order.name,
                        'partner_id': supplier.id,
                        'location_id': location_id,                        
                        'pricelist_id': supplier_pricelist.id,
                        'company_id': sale_order.company_id.id,
                        'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                        'sale_order_id':sale_order.id,
                        'warehouse_id':make.warehouse_id.id ,                      
            })
            new_ids.append(purchase_id)
            for line in sale_order.order_line:
                if line.product_id.sale_make_purchase == True:                
                    product = line.product_id
                    taxes_ids = product.supplier_taxes_id
                    taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                    purchase_order_line.create(cr, uid, {
                        'order_id': purchase_id,
                        'name': product.partner_ref,
                        'product_qty': line.product_uom_qty,
                        'product_id': product.id,
                        'product_uom': product.uom_po_id.id,
                        'price_unit': product.standard_price,
                        'date_planned': make.date_planned,
                        'taxes_id': [(6, 0, taxes)],
                    }, context=context)
        if not new_ids:
            return {'type': 'ir.actions.act_window_close'}
        if len(new_ids)<=1:
            value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
        else:
            value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'purchase.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
        return value
                
sale_make_purchase()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: