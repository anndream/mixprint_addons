# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 INECO Part., Ltd. (<http://www.ineco.co.th>).
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

class wizard_barcode_finding(osv.osv_memory):

    _name = 'wizard.barcode.finding'
    _description = 'Barcode Finding'
    _columns = {
        'code': fields.char('Code', size=32,),
        'note': fields.text('Description', ),
    }

    def open_popup(self, cr, uid, ids, context=None):
        res = {}
        #barcode_obj = self.pool.get('ineco.barcode')
        #data = self.read(cr, uid, ids, [], context=context)[0]
        #if data['code']:
        #    barcode = data['code']
        print "OK Printing"
        res = {'value': {'note':'123'}}
        return res
    
    def open_popup_origin(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'ineco_barcode', 'view_ineco_barcode_form')
        return {
            'name': 'Barcode Form',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res and res[1] or False],
            'res_model': 'ineco.barcode',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': 5  or False, ##please replace record_id and provide the id of the record to be opened 
        }
        
    def default_get(self, cr, uid, fields, context=None):
        res = super(wizard_barcode_finding, self).default_get(cr, uid, fields, context=context)
        #partner_id = self._find_matching_partner(cr, uid, context=context)

        #if 'action' in fields:
        #    res['action'] = partner_id and 'exist' or 'create'
        #if 'partner_id' in fields:
        #    res['partner_id'] = partner_id

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:   