# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITED (<http://www.ineco.co.th>).
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

{
    'name' : 'INECO CRM Dashboard',
    'version' : '0.1',
    'depends' : ['base','ineco_jasper_report'],
    'author' : 'Mr.Tititab Srisookco',
    'category': 'INECO',
    'description': """
    """,
    'website': 'http://www.ineco.co.th',
    'data': [],
    'update_xml': [
        'ineco_crm_dashboard_view.xml',
        'security.xml',
        'ineco_crm_data.xml',
    ],
    'js': ['static/src/js/*.js'],
    'css': ['static/src/css/*.css'],
    'qweb': ['static/src/xml/*.xml'],    
    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
