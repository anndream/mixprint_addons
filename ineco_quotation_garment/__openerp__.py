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
    'name' : 'Ineco Quotation for Garment',
    'version' : '0.2',
    'author' : 'Mr.Tititab Srisookco',
    'category' : 'INECO',
    'description' : """
New Quotation Menu/View for Garment Business.
- update view mail.email_compose_message_wizard_form 
  <!-- <field name="partner_ids" .... domain="[('is_user','=',1)]"/> -->

    """,
    'website': 'http://www.ineco.co.th',
    'images' : [],
    'depends' : ['base','sale','crm','ineco_crm','product',
                 'stock','sale_stock','account','hr','ineco_stock','purchase',
                 'account_cancel','mrp','mrp_operations','multi_image',
                 'ineco_thai_account'],
    'data': [
    ],
    'js': [
    ],
    'qweb' : [
    ],
    'css':[
           
    ],
    'demo': [
    ],
    'test': [
    ],
    'update_xml':[
        'wizard/wizard_pattern_copy_view.xml',
        'wizard/wizard_ticket_split_view.xml',
        'sale_view.xml',
        'stock_view.xml',
        'account_view.xml',
        'sale_data.xml',
        'stock_partial_picking_view.xml',
        'partner_view.xml',
        'problem_view.xml',
        'problem_data.xml',
        'res_users_view.xml',
        'invoice_view.xml',
        'security.xml',
        'product_view.xml',
        'dashboard_view.xml',
        'dashboard_invoice_view.xml',
        'pattern_view.xml',
        'mrp_view.xml',
        'wizard/wizard_update_production_start_view.xml',
        'wizard/wizard_start_workorder_view.xml',
        'wizard/wizard_done_workorder_view.xml',
        'wizard/wizard_pattern_select_view.xml',
        'wizard/wizard_update_otherinfo_view.xml',
        'wizard/wizard_update_routing_view.xml',
        'wizard/wizard_update_printmo_view.xml',
        'wizard/wizard_update_printplan_view.xml',
        'wizard/wizard_make_collar_view.xml',
        'wizard/wizard_collar_view.xml',
        'purchase_view.xml',
        'schedule_data.xml',
        'sequence.xml',
        'dashboard_warehouse_view.xml',
        'wizard/wizard_change_invoiced_view.xml',
        'wizard/wizard_prepare_commission_view.xml',
        'wizard/wizard_pay_commission_view.xml',
        'cheque_view.xml',
        'wizard/wizard_cheque_action_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
