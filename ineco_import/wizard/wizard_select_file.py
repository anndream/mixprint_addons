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
import csv
import base64
from cStringIO import StringIO
#import StringIO

#from openerp.tools.float_utils import float_round
#from openerp import SUPERUSER_ID
#import openerp.tools

class wizard_ineco_select_file(osv.osv_memory):
    _name = "wizard.ineco.select.file"
    _description = "Select file CSV to import"
    _columns = {
        'file_import': fields.binary(string='CSV File', required=True),
    }
    
    def import_file(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        csv_file = base64.decodestring(data['file_import'])
        f = StringIO(csv_file)
        reader = csv.reader(f, delimiter=',')      
        next(reader, None)
        pool_obj = pooler.get_pool(cr.dbname)
        line_obj = pool_obj.get('ineco.import.account.invoice.line')
        active_id = context['active_id']
        for line in reader:
            new_data = {
                'name': unicode(line[0], 'utf-8').strip(),
                'date': line[1].strip(),
                'supplier': unicode(line[2],'utf-8').strip(),
                'product':  unicode(line[4],'utf-8').strip(),
                'type': line[3],
                'vat': line[5],
                'total': line[6],
                'job_id': active_id,
            }
            line_obj.create(cr, uid, new_data)

        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: