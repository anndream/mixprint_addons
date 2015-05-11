# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITE (<http://www.ineco.co.th>).
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

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'pid': fields.char('Tax ID', sieze=32, select=True),   
        'billing_payment_id': fields.many2one('account.payment.term', 'Billing Term', select=True),
        'with_holding_type': fields.selection([('pp4','PP3'),('pp7','PP53')], 'With Holding Tax'),
        'tax_detail': fields.char('Tax Detail', size=256),
        'note_cheque': fields.char('Note Cheque', size=256),
        'cheque_payment_id': fields.many2one('account.payment.term', 'Cheque Term', select=True),
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: