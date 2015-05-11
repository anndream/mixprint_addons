# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD., Part. (<http://www.ineco.co.th>).
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

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'next_garment_order_no': fields.char('Garment Order No', size=32),
        'next_garment_order_date': fields.date('Garment Order Date'),
        'next_sample_order_no': fields.char('Sampling Order No', size=32),
        'candidate_ids': fields.one2many('sale.order.candidate','order_id','Candidates'),
    }
    
class sale_order_candidate(osv.osv):
    _name = 'sale.order.candidate'
    _description = "Candidate Material"
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'cost': fields.integer('Unit Price'),
        'order_id': fields.many2one('sale.order','Sale Order'),
    }
    _defaults = {
        'cost': 1.0,
    }