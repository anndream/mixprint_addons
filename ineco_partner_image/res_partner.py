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


#import datetime
#import math
#import openerp
from openerp.osv import osv, fields
#from openerp import SUPERUSER_ID
#import re
#from openerp import tools
import io
from PIL import Image
import StringIO
#from tools.translate import _
#import logging
#import pooler
#import pytz
#from lxml import etree

class res_partner(osv.osv):
    
    def _get_report_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.image:               
                image_stream = io.BytesIO(obj.image.decode('base64'))
                image = Image.open(image_stream)
                fp = StringIO.StringIO()
                image.save(fp,"JPEG")
                result[obj.id] = fp.getvalue()
        return result
    
    _inherit = "res.partner"
    _columns = {
        'image_report': fields.function(_get_report_image, 
            string="Report-sized image", type="binary",
            store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            })
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: