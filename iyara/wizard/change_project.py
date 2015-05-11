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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time

class iyara_change_project(osv.osv_memory):

    _name = "iyara.change.project"
    _description = "Iyara Change Project"
    _columns = {
                'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account',required=True, domain=[('type', '=', 'normal')]),        
                } 
 
    def change_project(self, cr, uid, ids, context=None):
        
        analytic_line_obj = self.pool.get('account.analytic.line')
        move_line_obj = self.pool.get('account.move.line')        
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        
        wizard = self.browse(cr, uid, ids[0], context)
        analytic_line_id = context.get('active_ids', [])
        analytic_line_browse = self.pool.get('account.analytic.line').browse(cr,uid,analytic_line_id)

        for analytic_line in analytic_line_browse:
            move_line_browse = self.pool.get('account.move.line').browse(cr,uid,[analytic_line.move_id.id])            
            for move_line in move_line_browse:
                invoice_ids = invoice_obj.search(cr,uid,[('move_id','=',move_line.move_id.id)])
                voucher_ids = voucher_obj.search(cr,uid,[('move_id','=',move_line.move_id.id)])
                if invoice_ids or voucher_ids:
                    analytic_line_obj.write(cr,uid,analytic_line_id,{'account_id': wizard.account_analytic_id.id})
                    move_line_obj.write(cr,uid,[move_line.id],{'analytic_account_id': wizard.account_analytic_id.id})
                if invoice_ids:
                    invoice_line_ids = invoice_line_obj.search(cr,uid,[('invoice_id','=',invoice_ids[0]),
                                                    ('account_analytic_id','=',analytic_line.account_id.id),
                                                    ('product_id','=',analytic_line.product_id.id),
                                                    ('account_id','=',analytic_line.general_account_id.id),
                                                    ('price_subtotal','=',abs(analytic_line.amount))])
                    
                    invoice_line_obj.write(cr,uid,invoice_line_ids,{'account_analytic_id': wizard.account_analytic_id.id})
                    
                if voucher_ids:
                    voucher_line_ids = voucher_line_obj.search(cr,uid,[('voucher_id','=',voucher_ids[0]),
                                                    ('account_analytic_id','=',analytic_line.account_id.id),
                                                    ('account_id','=',analytic_line.general_account_id.id),
                                                    ('amount','=',abs(analytic_line.amount))])
                    voucher_line_obj.write(cr,uid,voucher_line_ids,{'account_analytic_id': wizard.account_analytic_id.id})
                    
                    
            
        return {'type': 'ir.actions.act_window_close'}
        
        
        

iyara_change_project()    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: