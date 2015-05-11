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

from openerp.osv import fields, osv


class stock_picking(osv.osv):
    
    _inherit = "stock.picking"
    _description = "Picking List Iyara int"
    
    _columns = {
                'analytic_account_id': fields.many2one('account.analytic.account','Analytic account', domain=[('parent_id', '!=', False),('type','=','normal')],),
                }
    
stock_picking()

class stock_picking_in(osv.osv):
    
    _inherit = "stock.picking.in"
    _description = "Picking List Iyara in"
    _columns = {
                'analytic_account_id': fields.many2one('account.analytic.account','Analytic account', domain=[('parent_id', '!=', False),('type','=','normal')],),
                }
    
stock_picking_in()

class stock_picking_out(osv.osv):
    
    _inherit = "stock.picking.out"
    _description = "Picking List Iyara Out"
    _columns = {
                'analytic_account_id': fields.many2one('account.analytic.account','Analytic account', domain=[('parent_id', '!=', False),('type','=','normal')],),
                }

stock_picking_out()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: