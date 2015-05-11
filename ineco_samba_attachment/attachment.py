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

#import hashlib
#import itertools
import logging
import os
import re

from openerp import tools
from openerp.osv import fields,osv

_logger = logging.getLogger(__name__)

class ir_attachment(osv.osv):

    def _full_path(self, cr, uid, location, path):
        # location = 'file:filestore'
        assert location.startswith('file:'), "Unhandled filestore location %s" % location
        location = location[5:]

        # sanitize location name and path
        #location = re.sub('[.]','',location)
        #location = location.strip('/\\')

        path = re.sub('[.]','',path)
        path = path.strip('/\\')
        #os.path.join(tools.config['root_path'], location, cr.dbname, path)
        return os.path.join(location, cr.dbname, path)
  
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'samba.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'samba.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            super(ir_attachment, self).write(cr, uid, [id], {'store_fname': fname, 'file_size': file_size, 'location':location[5:]}, context=context)
        else:
            super(ir_attachment, self).write(cr, uid, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
     
    _inherit = 'ir.attachment'
    
    _columns = {
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
        'location': fields.char('Path', size=128),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        self.check(cr, uid, ids, 'unlink', context=context)
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'samba.location')
        if location:
            for attach in self.browse(cr, uid, ids, context=context):
                if attach.store_fname:
                    self._file_delete(cr, uid, location, attach.store_fname)
        return super(ir_attachment, self).unlink(cr, uid, ids, context)
    