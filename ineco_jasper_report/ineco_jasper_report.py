# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 INECO LTD, PARTNERSHIP (<http://www.ineco.co.th>).
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

import math

from osv import fields,osv
import tools
import pooler
from tools.translate import _
from decimal import *
import decimal_precision as dp
import netsvc

import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from operator import itemgetter
from itertools import groupby

from jasperclient import * 

import os
import M2Crypto

def _links_get(self, cr, uid, context=None):
    obj = self.pool.get('res.request.link')
    ids = obj.search(cr, uid, [], context=context)
    res = obj.read(cr, uid, ids, ['object', 'name'], context)
    return [('product.product','Product')]
    #return [(r['object'], r['name']) for r in res]
    # pool = pooler.get_pool(cr.dbname)
    # dbuuid = pool.get('ir.config_parameter').get_param(cr, uid, 'database.uuid')

class ineco_jasper_server(osv.osv):
    
    _public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDh1p8F+XZGlZbtCIyLMUab7oMz
WMucDj+GXZtkXpUSI3EC6Te7F7wMY6lPphiu8DhpiBF38yiuFpzBuAvHJbEOBfW8
+UXU6pEEL87sNKI7UsHZxFv4iIlGcC0i/7QBVR4DLhM5GGu4gc+Vg6yhzzjymQIm
npxHqLH2SWP9D8t1jwIDAQAB
-----END PUBLIC KEY-----"""

    def _get_code1(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for id in ids:
            bio = M2Crypto.BIO.MemoryBuffer(self._public_key)
            WriteRSA = M2Crypto.RSA.load_pub_key_bio(bio)
            uuid = self.pool.get('ir.config_parameter').get_param(cr, uid, 'database.uuid')
            encrypt_text = WriteRSA.public_encrypt(uuid.encode('ascii'), M2Crypto.RSA.pkcs1_oaep_padding)
            res[id] = encrypt_text.encode('base64')
        
        return res

    def _get_code2(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids):            
            bio = M2Crypto.BIO.MemoryBuffer(data.key1.encode('ascii'))
            ReadRSA = M2Crypto.RSA.load_key_bio(bio)
            PlainText = ReadRSA.private_decrypt (data.passportkey.decode('base64'), M2Crypto.RSA.pkcs1_oaep_padding)
            res[data.id] = PlainText
        return res

    def _get_uuid(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = self.pool.get('ir.config_parameter').get_param(cr, uid, 'database.uuid')
            
        return res
    
    _name = 'ineco.jasper.server'
    _description = 'Ineco Jasper Server'
    _columns = {
        'name': fields.char('Host URL', size=250, required=True),
        'host': fields.char('Host IP', size=32, required=True),
        'port': fields.integer('Port', required=True),
        'username': fields.char('User Name', size=250, required=True),
        'password': fields.char('Password', size=250, required=True),
        'dir': fields.char('Folder', size=250, required=True),
        'uuid': fields.function(_get_uuid, method=True, type="char", string="UUID"),
        'key1': fields.text('Private Key', readonly=True),
        'key2': fields.text('Public Key', readonly=True),
        'code1': fields.function(_get_code1, method=True,  string="CODE", type='text'),
        'code2': fields.function(_get_code2, method=True,  string="UUID2", type='char'),
        'passportkey': fields.text('Passport Key'),
        'passport': fields.char('Passport', size=250),        
        'report_ids': fields.one2many('ineco.jasper.report','server_id','Reports'),
    }
    _defaults = {
        'dir': "/reports/samples",
        'port': 8000,
        'host': '127.0.0.1',
        'name': 'http://127.0.0.1:8000/jasperserver/services/repository?wsdl',
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name, dir)', 'Host and Folder must be unique!'),
    ]
    _order = 'name'
    
    def create(self, cr, uid, vals, context=None):
        Bob = M2Crypto.RSA.gen_key (1024, 65537)
        Bob.save_key ('private.pem', None)
        Bob.save_pub_key ('public.pem')
        key1 = open('private.pem').read()
        key2 = open('public.pem').read()
        vals.update({'key1':key1,'key2':key2})
        return super(ineco_jasper_server, self).create(cr, uid, vals, context=context)

    def button_get_report(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        report_obj = self.pool.get('ineco.jasper.report')
        for line in self.browse(cr, uid, ids):
            JC = Client(line.name, username=line.username, password=line.password)
            req = createRequest(
                uriString=line.dir, 
                wsType="folder", 
                operationName="list")
            res = JC.service.list(req)
            res = res.encode('utf-8')
            #for rd in ET.fromstring(res).findall('resourceDescriptor'):
            for rd in ET.fromstring(res).findall('resourceDescriptor'):
                if rd.get('wsType') == 'reportUnit':
                    thislabel = rd.findall('label')[0]
                    description = rd.findall('description')[0]
                    data = {
                        'name': rd.get('name'),
                        'uristring': rd.get('uriString'),
                        'label': description.text or thislabel.text,
                        'server_id': line.id,
                    }
                    if not report_obj.search(cr, uid, [('name','=',rd.get('name'))]):
                        report_id = report_obj.create(cr, uid, data)
                        for report in self.pool.get('ineco.jasper.report').browse(cr, uid, [report_id]):
                            report.button_check_param()
                        
        return True
    
ineco_jasper_server()

class ineco_jasper_report(osv.osv):
    
    _name = 'ineco.jasper.report'
    _description = 'Ineco Jasper Report Engine'
    _columns = {
        'name': fields.char('Name', size=250, required=True),
        'uristring': fields.char('uriString', size=250, required=True),
        'label': fields.char('Label', size=250, required=True),
        'server_id': fields.many2one('ineco.jasper.server', 'Server', ondelete="restrict"),
        'param_ids': fields.one2many('ineco.jasper.report.params','report_id','Parameters'),
        'module': fields.selection([('sale', 'Sale'),
                                   ('purchase', 'Purchase'),
                                   ('mrp', 'Manufacturing'),
                                   ('account', 'Account'),
                                   ('warehouse', 'Warehouse')], 'Module' ),
        'group_ids': fields.many2many('res.groups', 'jasperreport_group_rel', 'jasperreport_id', 'group_id', 'Groups'),                
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name, server_id, uristring)', 'Server and Report must be unique!'),
    ]
    _order = 'server_id, name'
    
    def browse_report(self, cr, uid, ids, *args):
        if not ids:
            return False
        pattern = "http://%s:%s/jasperserver/flow.html?_flowId=viewReportFlow&reportUnit=%s&j_username=%s&j_password=%s&userLocale=en&current_user_id=%s"
        report =  self.browse(cr, uid, ids)[0]
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        final_url = pattern % (
                        report.server_id.host, 
                        report.server_id.port,
                        report.uristring,
                        report.server_id.username,
                        report.server_id.password,
                        uid )
        url_link = {
            'type': 'ir.actions.act_url',
            'url':final_url,
            'target': 'new'
        }
        return url_link

    def button_check_param(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        report_obj = self.pool.get('ineco.jasper.report.params')
        for line in self.browse(cr, uid, ids):
            JC = Client(line.server_id.name, username=line.server_id.username, password=line.server_id.password)
            req = createRequest(
                uriString=line.uristring, 
                wsType="reportUnit", 
                operationName="list")
            res = JC.service.list(req)
            res = res.encode('utf-8')
            for rd in ET.fromstring(res).findall('resourceDescriptor'):
                if rd.get('wsType') == 'inputControl':
                    thislabel = rd.findall('label')[0]
                    data = {
                        'param_name': rd.get('name'),
                        'param_uristring': rd.get('uriString'),
                        'param_label': thislabel.text,
                        'report_id': line.id,
                    }
                    if not report_obj.search(cr, uid, [('param_name','=',rd.get('name'))]):
                        report_obj.create(cr, uid, data)
        
        return True
    
ineco_jasper_report()

class ineco_jasper_report_params(osv.osv):
    
    _name = 'ineco.jasper.report.params'
    _description = 'Ineco Jasper Report Parameter'
    _columns = {
        'param_name': fields.char('Name', size=250, required=True),
        'param_uristring': fields.char('uriString', size=250, required=True),
        'param_label': fields.char('Label', size=250, required=True),
        'reference_id':fields.reference('Document', selection=_links_get, size=128),        
        'report_id': fields.many2one('ineco.jasper.report', 'Report', ondelete="cascade"),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(param_name,report_id)', 'Report and Parameters must be unique!'),
    ]
    
ineco_jasper_report_params()
