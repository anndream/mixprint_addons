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

# 2014-01-24    POP-1    Bug in stock date datetime

import datetime
import time

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import tools

import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def button_cancel_mrp(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            sale_obj = self.browse(cr, uid, ids)[0]
            production_obj = self.pool.get('mrp.production')
            production_ids = production_obj.search(cr, uid, [('origin','=',sale_obj.name)])
            for prod_id in production_ids:
                prod_name = production_obj.browse(cr, uid, prod_id).name
                production_obj.write(cr, uid, prod_id, {'name': prod_name+'#CN'+time.strftime('%Y-%m-%d %H:%M:%S') })
                wf_service.trg_validate(uid, 'mrp.production', prod_id, 'button_cancel', cr) 
        return True
    
    def button_delete_picking(self, cr, uid, ids, context=None):
        for id in ids:
            sql = """
                delete from stock_move
                where picking_id in (select id from stock_picking
                  where sale_id = %s)
            """
            cr.execute(sql % (id))
            sql = """
                delete from stock_picking
                where sale_id = %s         
            """
            cr.execute(sql % (id))
        return True

    def button_toggle_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def button_toggle_progress(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'progress'})
        return True

    def button_toggle_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'})
        return True
    
    def button_change_draft(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        self.button_delete_picking(cr, uid, ids, context)
        self.button_cancel_mrp(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for doc_id in ids:
            cr.execute("select id from wkf where osv = '"+'sale.order'+"'")
            wkf_ids = map(lambda x: x[0], cr.fetchall())
            wkf_id = wkf_ids[0]
            cr.execute("select id from wkf_activity where wkf_id = %s and name = 'draft'" % (wkf_id))
            act_ids = map(lambda x: x[0], cr.fetchall())
            act_id = act_ids[0]
            cr.execute('update wkf_instance set state=%s where res_id=%s and res_type=%s', ('active', doc_id, 'sale.order'))
            cr.execute("update wkf_workitem set state = 'active', act_id = %s where inst_id = (select id from wkf_instance where wkf_id = %s and res_id = %s)", (str(act_id), str(wkf_id), doc_id))
        
        return True
    