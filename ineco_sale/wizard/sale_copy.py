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

class ineco_sale_copy(osv.osv_memory):
    _name = "ineco.sale.copy"
    _description = "Sale Copy"

    _columns = {
        'shop_id': fields.many2one('sale.shop','Shop', required=True),
    }
    
    def create_sale(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids)[0]
        default = {}
        default['name'] = '/'
        default['shop_id'] = data.shop_id.id    
        for id in context['active_ids']:
            sale_obj = self.pool.get('sale.order').browse(cr, uid, id)
            default['origin'] = sale_obj.name
            if sale_obj.shop_id.id != data.shop_id.id:
                context['change_shop'] = True
            self.pool.get('sale.order').copy(cr, uid, sale_obj.id, default=default, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
    