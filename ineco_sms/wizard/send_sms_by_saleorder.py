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

from openerp.osv import fields, osv
#import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import tools

class sms_send_by_saleorder(osv.osv_memory):
    _name = "sms.send.by.saleorder"
    _description = "Send SMS in sale order."
    _columns = {
        'server_id' : fields.many2one('ineco.sms.server', 'Server', required=True),
        'phone': fields.char('Mobile No', size=64, required=True),
        'message': fields.text('Message'),        
    }

#    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#        if context is None: context = {}
#        fvg = super(sms_send_by_saleorder, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
#        sale_id = context and context.get('active_id', False) or False
#
#        if view_type == 'form' and (context.get('active_model') == 'sale.order') and sale_id:
#            sale_obj = self.pool.get('sale.order').browse(cr, uid, sale_id, context=context)
#            fvg['fields']['Mobile No'] =  sale_obj.partner_id.mobile
#
#        return fvg

    def default_get(self, cr, uid, fields, context):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        res = super(sms_send_by_saleorder, self).default_get(cr, uid, fields, context=context)
        server_ids = self.pool.get('ineco.sms.server').search(cr, uid,[('is_default','=',True)])
        if server_ids:
            res.update({'server_id': server_ids[0]})
        sale_id = context and context.get('active_id', False) or False
        if (context.get('active_model') == 'sale.order') and sale_id:
            sale_obj = self.pool.get('sale.order').browse(cr, uid, sale_id, context=context)
            if 'phone' in fields:
                res.update({'phone': sale_obj.partner_id.mobile or False})

        return res

    def send_sms(self, cr, uid, ids, context=None):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context')

        for data in self.browse(cr, uid, ids, context=context):
            if data.server_id.balance < 1:
                raise osv.except_osv(_('Warning!'), _('Balance limited.'))
            data.server_id.send_message(data.phone,data.message)
        return {}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4::