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

#import time
#from datetime import datetime

#import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
#from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
#from openerp.tools import float_compare
#from openerp.tools.translate import _
#from openerp import netsvc
from openerp import tools

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'shipping_term': fields.char('Shipping Term',size=100),
        'shipping_via': fields.char('Shippint Via', size=100),
        'incoterm': fields.char('FOB',size=100)
    }