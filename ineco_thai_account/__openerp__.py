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


{
    'name' : 'INECO THAI Accounting',
    'version' : '0.1',
    'depends' : ["base","sale","account","account_voucher","hr","stock","ineco_stock"],
    'author' : 'INECO LTD.,PART.',
    'category': 'Accounting',
    'description': """
Feature: 
A. Sale Module:
1. Add Delivery Date on Sale Order
2. Add Delivery Method on Sale Order
3. Add Exchange Rate on Sale Order
    """,
    'website': 'http://www.ineco.co.th',
    'data': [
        'wht_data.xml',
        'sequence.xml',
    ],
    'update_xml': [
        'res_partner_view.xml',
        'delivery_view.xml',
        'wizard/sale_make_invoice_advance.xml',
        'sale_view.xml',
        'invoice_view.xml',
        'wht_view.xml',
        'report_view.xml',
        'cheque_view.xml',
        'res_company_view.xml',
        'close_account_view.xml',
        'journal_view.xml',
        'stock_view.xml',
        'security.xml',
        'account_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
