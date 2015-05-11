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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
#from openerp import pooler
from openerp.osv import fields, osv
#from openerp.tools.translate import _
#from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import openerp.addons.decimal_precision as dp
#from openerp import netsvc

class crm_helpdesk(osv.osv):
    _inherit = "crm.helpdesk"
    _columns = {
        'contract_id': fields.many2one('iyara.contract','Contract'),
        'picking_id': fields.many2one('stock.picking','Picking'),
        'project_id': fields.many2one('account.analytic.account','Project')
    }
    _order = "date, id"

class iyara_type_task(osv.osv):
    _name = 'iyara.type.task'
    _columns = {
        'name': fields.char('Code', size=16,required=True),
        'description': fields.char('Description',size=128,required=True),
    }    

class iyara_controlpanel(osv.osv):
    _name = 'iyara.type'
    _columns = {
        'name': fields.char('Control Panel', size=64, required=True),
        'type': fields.selection([('panel','Control Panel'),('avr','AVR Model'),('batter','Battery'),('charger','Charger')],'Type')
    }

class iyara_contract(osv.osv):
    _name = 'iyara.contract'
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Contract No', size=42,required=True),
        'saleorder_id': fields.many2one('sale.order', 'Sale Order'),
        'customer_id': fields.many2one('res.partner','Customer',domain=[('customer','=',1)],required=True),
        'street': fields.char('Address', size=128, required=True),
        'phone': fields.char('Phone', size=32),
        'fax': fields.char('Fax', size=32),
        'project_id': fields.many2one('account.analytic.account','Project'),
        'installation': fields.char('Installation Address',size=128,required=True),
        'zone': fields.char('Zone',size=32),
        'gps': fields.char('GPS',size=64),
        'supplier_id': fields.many2one('res.partner','Supplier',domain=[('supplier','=',1)]),
        'gen_model': fields.char('Gen Model', size=128,required=True),
        'gen_sn': fields.char('Gen S/N', size=64, required=True),
        'alternator_model': fields.char('Alternator Model', size=64, required=True),
        'alternator_sn': fields.char('Alternator S/N', size=64, required=True),
        'engine_model': fields.char('Engine Model', size=64, required=True),
        'engine_sn': fields.char('Engine S/N', size=64, required=True),
        'controlpanel_id': fields.many2one('iyara.type','Control Panel',domain=[('type','=','panel')]),
        'avr_id': fields.many2one('iyara.type','AVR Model',domain=[('type','=','avr')]),
        'battery_id': fields.many2one('iyara.type','Battery Type',domain=[('type','=','battery')]),
        'battery_charger_id': fields.many2one('iyara.type','Charger Type',domain=[('type','=','charger')]),
        'battery_qty': fields.integer('Battery Qty'),
        'gift_qty': fields.integer('Gift Qty'),
        'date_contract_start': fields.date('Date Contract Start', required=True),
        'date_contract_finish': fields.date('Date Contract Finish', required=True),
        'date_contract_first': fields.date('Date Contract First', required=True),
        'warranty_qty': fields.integer('Warranty Qty'),
        'service_qty': fields.integer('Service Qty'),
        'helpdesk_ids': fields.one2many('crm.helpdesk','contract_id','Task'),
        'type_task_id': fields.many2one('iyara.type.task','Type Task'),
    }
    
    _defaults = {
        'name': '/',
        'service_qty':1,
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'iyara.contract') or '/'
        result = super(iyara_contract, self).create(cr, uid, vals, context=context)
        return result
    
    def button_genhelpdesk(self, cr, uid, ids, context=None):
        helpdesk_obj = self.pool.get('crm.helpdesk')
        date_length = 30
        for contract in self.browse(cr, uid, ids):
            if contract.date_contract_first and contract.date_contract_finish and contract.service_qty:
                date_start = datetime.strptime(contract.date_contract_first, '%Y-%m-%d')
                date_finish = datetime.strptime(contract.date_contract_finish, '%Y-%m-%d')                
                date_length = int((date_finish - date_start).days / contract.service_qty)
                #print date_length
            default_prefix = contract.type_task_id and contract.type_task_id.name + '. ' or 'No.'
            default_prefix = default_prefix + (contract.project_id and contract.project_id.name or '')+' '
            for i in range(contract.service_qty):
                helpdesk_data = {
                    'name': default_prefix+str(i+1)+'/'+str(contract.service_qty),
                    'contract_id': contract.id,
                    'partner_id': contract.customer_id.id,
                    'date': date_start.strftime('%Y-%m-%d 00:00:00')
                }
                date_start = date_start + timedelta(days=date_length)
                helpdesk_obj.create(cr, uid, helpdesk_data)
        return True
