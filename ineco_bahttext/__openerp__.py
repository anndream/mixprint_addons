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
{
    'name' : 'Ineco Baht Text',
    'version' : '0.1',
    'author' : 'INECO Part.,Ltd.',
    'category': 'Tools',
    'website' : 'http://www.ineco.co.th',
    'summary' : 'Convert numeric to bath text',
    'description' : """
1. Add function bahttext(numeric) to postgresql

Please update bahttext.sql again after install it.
""",
    'depends' : [
        'base',
    ],
    'data' : [
    ],
    'update_xml' : [
    ],
    'installable' : True,
    'application' : False,
}
