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
    'name' : 'INECO CRM Extended',
    'version' : '0.1',
    'depends' : ['base','crm','crm_todo','project','sale','sale_crm','ineco_partner'],
    'author' : 'Mr.Tititab Srisookco',
    'category': 'INECO',
    'description': """
    """,
    'website': 'http://www.ineco.co.th',
    'data': [],
    'update_xml': [
        'security/crm_security.xml',
        'crm_view.xml',
        'res_partner_view.xml',
        'schedule_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
