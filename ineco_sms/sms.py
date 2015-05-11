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

import time
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
#from operator import itemgetter

#import logging
#import openerp.pooler
from openerp.osv import fields, osv
#import openerp.addons.decimal_precision as dp
#from openerp.tools.translate import _
#from openerp.tools.float_utils import float_round
#from openerp import SUPERUSER_ID
#import openerp.tools

import httplib, urllib
import xml.etree.ElementTree as ET

class ineco_sms_server(osv.Model):
    _name = 'ineco.sms.server'
    _description = 'SMS Server'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
        'name': fields.char('Server Path',size=255, reqruied=True),
        'port': fields.integer('Port', required=True),
        'uri': fields.char('URI', size=255, required=True),       
        'username': fields.char('User Name', size=25, required=True),
        'password': fields.char('Password', size=25, required=True), 
        'balance': fields.integer('Balance'),
        'log_ids': fields.one2many('ineco.sms.log', 'server_id', 'Logs'),
        'is_default': fields.boolean('Default'),
    }
    _defaults = {
        'port': 80,
        'name': 'www.thaibulksms.com',
        'uri': '/sms_api.php',
        'balance': 0,
        'is_default': True,
    }
    _order = "is_default"
    
    def get_balance(self, cr, uid, ids, context=None):
        
#            Argruments:
#            (string) username --- ThaiBulkSMS username (required)
#            (string) password --- ThaiBulkSMS password (required)
#            (string) tag --- "credit_remain" for standard SMS or "credit_remain_premium" for premium SMS
        
        for server in self.browse(cr, uid, ids):
            conn = httplib.HTTPConnection(server.name, server.port)
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            params = urllib.urlencode({'username': server.username, 'password': server.password, 'tag': 'credit_remain' })
            
            conn.request("POST", server.uri, params, headers)
            response = conn.getresponse()
            data = response.read()
            
            conn.close()
            
            sms_log = self.pool.get('ineco.sms.log')
            log = {}
            if response.status == 200:
                log = {
                    'server_id': server.id,
                    'phone': 'Check Balance',
                    'message': '',
                    'status': response.status,
                    'reason': data,
                    'date_send': time.strftime('%Y-%m-%d %H:%M:%S'),
                }
            else:
                log = {
                    'server_id': server.id,
                    'phone': 'Unreachable',
                    'message': '',
                    'status': response.status,
                    'reason': response.reason,
                    'date_send': time.strftime('%Y-%m-%d %H:%M:%S'),
                }
            sms_log.create(cr, uid, log)
            if data.isalnum():
                server.write({'balance':data})
            
        return True

    def send_message(self, cr, uid, ids, phones, message, context=None):
        
        for server in self.browse(cr, uid, ids):
            conn = httplib.HTTPConnection(server.name, server.port)
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            params = urllib.urlencode({'username': server.username, 'password': server.password, 'msisdn': phones, 'message': message.encode('cp874')  })
            
            conn.request("POST", server.uri, params, headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
            
            sms_log = self.pool.get('ineco.sms.log')
            log = {}
            if response.status == 200:
                log = {
                    'server_id': server.id,
                    'phone': phones,
                    'message': message,
                    'status': response.status,
                    'reason': data,
                    'date_send': time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                root = ET.fromstring(data)
                if len(root):                    
                    for QUEUE in root.findall('QUEUE'):
                        for SMS in QUEUE.findall('RemainCredit'):
                            server.write({'balance': SMS.text})                        
            else:
                log = {
                    'server_id': server.id,
                    'phone': 'Unreachable',
                    'message': message,
                    'status': response.status,
                    'reason': response.reason,
                    'date_send': time.strftime('%Y-%m-%d %H:%M:%S'),
                }
            sms_log.create(cr, uid, log)
            
        return True

class ineco_sms_log(osv.Model):
    _name = 'ineco.sms.log'
    _description = 'SMS Log'
    _columns = {
        'name': fields.char('Description', size=64),
        'server_id': fields.many2one('ineco.sms.server','Server'),
        'date_send': fields.datetime('Date Send', select=True),
        'phone': fields.char('Phone No', size=64, select=True),
        'message': fields.char('Message', size=255, select=True),
        'status': fields.char('Status', size=128, select=True),
        'reason': fields.text('Note'),
        'seconds': fields.integer('Total Seconds'),
    }
    _defaults = {
        'seconds': 0,
    }
    _order = "date_send desc"
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4::