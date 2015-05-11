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

#import datetime

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class wizard_cheque_action(osv.osv_memory):
    
    _name = 'wizard.cheque.action'
    _description = 'Wizard Cheque Action'
    _columns = {
        #'is_print': fields.boolean('Print MO'),
    }
    
    def button_assign(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        for cheque in self.pool.get('ineco.cheque').browse(cr, uid, active_ids):
            if cheque.state == 'draft':
                cheque.write({"state":"assigned"})
        return {'type': 'ir.actions.act_window_close'}

    def button_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids',[])
        for cheque in self.pool.get('ineco.cheque').browse(cr, uid, active_ids):
            if cheque.state == 'assigned':
                cheque.write({"state":"done"})
        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
