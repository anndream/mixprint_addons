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

from datetime import datetime
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv

class purchase_order(osv.osv):
    
    _inherit = "purchase.order"
    _description = "TERMS & Sale BY"
    _columns = {
        'sale_by': fields.char('BY', size=64,),
        'iraya_terms': fields.selection([('ex_china','Ex-Warehouse China'),
                                         ('ex_singapore','Ex-Warehouse Singapore'),
                                         ('tt_advance','T/T in advance.')],'TERMS'),
        'review':fields.boolean('review', readonly=True, select=True, ),
        }
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft','shipped':0,'review':True,})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'purchase.order', p_id, cr)
            wf_service.trg_create(uid, 'purchase.order', p_id, cr)
        return True    
    
    
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
