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

#from lxml import etree
#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import datetime
import time
#from operator import itemgetter
#from itertools import groupby

from openerp.osv import fields, osv
#from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
#from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def action_done_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        cr.execute('select id from stock_move where picking_id in %s ', (tuple(ids),))
        move_ids = map(lambda x: x[0], cr.fetchall())
        self.write(cr, uid, ids, {'state': 'draft'})
        self.pool.get('stock.move').write(cr, uid, move_ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for doc_id in ids:
            cr.execute("select id from wkf where osv = '"+'stock.picking'+"'")
            wkf_ids = map(lambda x: x[0], cr.fetchall())
            wkf_id = wkf_ids[0]
            cr.execute("select id from wkf_activity where wkf_id = %s and name = 'confirmed'" % (wkf_id))
            act_ids = map(lambda x: x[0], cr.fetchall())
            act_id = act_ids[0]
            cr.execute('update wkf_instance set state=%s where res_id=%s and res_type=%s', ('active', doc_id, 'stock.picking'))
            cr.execute("update wkf_workitem set state = 'active', act_id = %s where inst_id = (select id from wkf_instance where wkf_id = %s and res_id = %s)", (str(act_id), str(wkf_id), doc_id))
        
        return True
    
class stock_picking_in(osv.osv):
    _inherit = 'stock.picking.in'
    
    def action_done_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        cr.execute('select id from stock_move where picking_id in %s ', (tuple(ids),))
        move_ids = map(lambda x: x[0], cr.fetchall())
        self.write(cr, uid, ids, {'state': 'draft'})
        self.pool.get('stock.move').write(cr, uid, move_ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for doc_id in ids:
            cr.execute("select id from wkf where osv = '"+'stock.picking'+"'")
            wkf_ids = map(lambda x: x[0], cr.fetchall())
            wkf_id = wkf_ids[0]
            cr.execute("select id from wkf_activity where wkf_id = %s and name = 'confirmed'" % (wkf_id))
            act_ids = map(lambda x: x[0], cr.fetchall())
            act_id = act_ids[0]
            cr.execute('update wkf_instance set state=%s where res_id=%s and res_type=%s', ('active', doc_id, 'stock.picking'))
            cr.execute("update wkf_workitem set state = 'active', act_id = %s where inst_id = (select id from wkf_instance where wkf_id = %s and res_id = %s)", (str(act_id), str(wkf_id), doc_id))
        
        return True    
    
class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    
    def action_done_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        cr.execute('select id from stock_move where picking_id in %s ', (tuple(ids),))
        move_ids = map(lambda x: x[0], cr.fetchall())
        self.write(cr, uid, ids, {'state': 'draft'})
        self.pool.get('stock.move').write(cr, uid, move_ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for doc_id in ids:
            cr.execute("select id from wkf where osv = '"+'stock.picking'+"'")
            wkf_ids = map(lambda x: x[0], cr.fetchall())
            wkf_id = wkf_ids[0]
            cr.execute("select id from wkf_activity where wkf_id = %s and name = 'confirmed'" % (wkf_id))
            act_ids = map(lambda x: x[0], cr.fetchall())
            act_id = act_ids[0]
            cr.execute('update wkf_instance set state=%s where res_id=%s and res_type=%s', ('active', doc_id, 'stock.picking'))
            cr.execute("update wkf_workitem set state = 'active', act_id = %s where inst_id = (select id from wkf_instance where wkf_id = %s and res_id = %s)", (str(act_id), str(wkf_id), doc_id))
        
        return True    
    