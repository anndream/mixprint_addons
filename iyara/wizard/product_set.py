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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time

class iyara_product_set(osv.osv_memory):
    
    _name = "iyara.product.set"
    _description = "Iyara Product Set"
    _columns = {
                'set_bom_id': fields.many2one('mrp.bom', 'Bill of Materials', domain=[('bom_id', '=', False)], required=True,),
                'qtty': fields.float('Quantity', digits=(16, 2), required=True),
                'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account', domain=[('type', '=', 'normal'),('end_project', '=', False)]),        
                } 
       
    _defaults = {
        'qtty': 1.0,
    }

    def create_sale_line(self, cr, uid, ids, context=None):
        sale_line_obj = self.pool.get('sale.order.line')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])
        bom_line_ids = self.pool.get('mrp.bom').search(cr, uid, [('bom_id','=',wizard.set_bom_id.id)])
        bom_line_ojb = self.pool.get('mrp.bom').browse(cr,uid,bom_line_ids,context)
        for line in bom_line_ojb:
            product_name = self.pool.get('product.product').name_get(cr, uid, [line.product_id.id], context)[0][1]
            if line.product_id.description_sale:
                product_name += '\n'+line.product_id.description_sale
           
            qty = (line.product_qty * wizard.qtty) or 0.00
            vals = {
                    'order_id': sale_ids[0],
                    'name': product_name,
                    'product_id': line.product_id.id,
                    'account_analytic_id': wizard.account_analytic_id.id,
                    'product_uom_qty': qty,
                    'product_uom': line.product_uom.id,
                    'product_uos_qty': qty, 
                    'price_unit': line.product_id.list_price or 0.00,
                    }            
            sale_line_id = sale_line_obj.create(cr, uid, vals, context=context)
            cr.execute('insert into sale_order_tax (order_line_id,tax_id) \
                            values (%s,%s)', (sale_line_id, 2))        
        return {'type': 'ir.actions.act_window_close'}
    
iyara_product_set()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: