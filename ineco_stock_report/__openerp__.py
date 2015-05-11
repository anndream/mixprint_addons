# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2014 Ineco Part., Ltd. (<http://www.ineco.co.th>).
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
    "name" : "Ineco Stock Report",
    "version" : "0.1",
    "description" : """
1. Add Incoming Form
2. Add Issue Form
3. Add Transfer Form
4. Add Delivery Form
    """,
    "author" : "Mr.Tititab Srisookco",
    "website" : "http://www.ineco.co.th",
    "depends" : ["base","jasper_reports","stock","ineco_stock"],
    "category" : "Generic Modules/Jasper Reports",
    "init_xml" : [],
    "demo_xml" : [ 
    ],
    "update_xml" : [
        'stock_report_view.xml'
    ],
    "active": False,
    "installable": True
}

