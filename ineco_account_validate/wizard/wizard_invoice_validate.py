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

#import time
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
#from operator import itemgetter

#import logging
#import openerp.pooler
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _

#from openerp.tools.float_utils import float_round
#from openerp import SUPERUSER_ID
#import openerp.tools

class account_move_confirm(osv.osv_memory):
    _name = "account.move.confirm"
    _description = "Confirm selected entry"
    
    def entry_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        pool_obj = pooler.get_pool(cr.dbname)
        data_inv = pool_obj.get('account.move').read(cr, uid, context['active_ids'], ['state'], context=context)
        entry = pool_obj.get('account.move')

        for record in data_inv:
            if record['state'] in ('draft'):
                entry_obj = entry.browse(cr, uid, record['id'])
                entry_obj.button_validate()
        return {'type': 'ir.actions.act_window_close'}
    

class account_voucher_confirm(osv.osv_memory):
    _name = "account.voucher.confirm"
    _description = "Confirm selected voucher"
    
    def voucher_confirm(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        if context is None:
            context = {}
        pool_obj = pooler.get_pool(cr.dbname)
        data_inv = pool_obj.get('account.voucher').read(cr, uid, context['active_ids'], ['state'], context=context)

        for record in data_inv:
            if record['state'] in ('draft'):
                wf_service.trg_validate(uid, 'account.voucher', record['id'], 'proforma_voucher', cr)
        return {'type': 'ir.actions.act_window_close'}


class account_invoice_confirm(osv.osv_memory):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _inherit = "account.invoice.confirm"
    _description = "Overide Confirm the selected invoices"

    def invoice_confirm(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        if context is None:
            context = {}
        pool_obj = pooler.get_pool(cr.dbname)
        data_inv = pool_obj.get('account.invoice').read(cr, uid, context['active_ids'], ['state'], context=context)

        for record in data_inv:
            if record['state'] in ('draft','proforma','proforma2'):
                wf_service.trg_validate(uid, 'account.invoice', record['id'], 'invoice_open', cr)
        return {'type': 'ir.actions.act_window_close'}