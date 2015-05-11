# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv, fields

class res_company(osv.osv):
    _inherit = "res.company"
    _description = 'address for vat thai'
    _columns = {
        'ineco_company_name': fields.char('Company Name', size=128),                
        'ineco_branch': fields.char('Branch', size=32),
        'ineco_building':fields.char('Building', size=128),
        'ineco_room_no':fields.char('Room No.', size=32),
        'ineco_class':fields.char('Class', size=32),
        'ineco_village':fields.char('Village', size=128),
        'ineco_no':fields.char('No.', size=32),
        'ineco_moo':fields.char('Moo.', size=32),
        'ineco_alley':fields.char('Alley', size=128),
        'ineco_road':fields.char('Road', size=128),
        'ineco_district':fields.char('District', size=128),
        'ineco_amphoe':fields.char('Amphoe', size=128), 
        'ineco_province':fields.char('Province.', size=128),       
        'ineco_zip':fields.char('Zip.', size=32),    
        'ineco_phone':fields.char('Phone', size=32),
        'ineco_tax':fields.char('Tax ID', size=32),    
        'ineco_position':fields.char('Position', size=128),
        'ineco_name':fields.char('Name', size=128),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
