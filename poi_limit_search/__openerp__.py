# -*- coding: utf-8 -*-
##############################################################################
#    
#    Poiesis Consulting, OpenERP Partner
#    Copyright (C) 2013 Poiesis Consulting (<http://www.poiesisconsulting.com>).
#    Author: Grover Menacho
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
    'name': 'Limit search Configuration',
    'version': '2.0',
    'category': 'Other',
    'sequence': 3,
    'summary': 'It allows to set limits on search',
    'description': """
Limit search configuration
===================================
Created by Poiesis Consulting
    """,
    'author': 'Poiesis Consulting - Grover Menacho',
    'website': 'http://www.poiesisconsulting.com',
    'depends': ['base','web','base_setup'],
    'data': ['res_config_view.xml'],
    'installable': True,
    'active': False,
    'application': True,
    'js': [
        'static/src/js/limit_search.js',
    ],

#    'certificate': 'certificate',
}