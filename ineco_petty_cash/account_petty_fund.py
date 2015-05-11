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

import decimal_precision as dp

from osv import osv, fields
import time
import datetime
from mx import DateTime
from tools.translate import _
import netsvc
import re
#from pprint import pprint
#from ac_utils import num2word, check_sum_pin, check_sum_tin, compute_discount, check_discount_fmt, one2many_dom

class account_petty_fund(osv.osv):
    _name="account.petty.fund"
    _order="name"

    def name_search(self, cr, uid, name='', args=[], operator='ilike', context=None, limit=80):
        fund_ids = []

        if name:
            fund_ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
        if not fund_ids:
            return super(account_petty_fund, self).name_search(cr, uid, name=name, args=args, operator=operator, context=context, limit=limit)
        else:
            return self.name_get(cr, uid, fund_ids)

    def _balance(self,cr,uid,ids,name,arg,context=None):
        vals={}
        for fund in self.browse(cr,uid,ids):
            amt=0.0
            for move in fund.moves:
                #if move.state!="posted":
                    #continue

                if move.type=='in':
                    amt+=move.amount
                else:
                    amt-=move.amount
            vals[fund.id]=amt
        return vals

    _columns={
        "name": fields.char("Name", size=64, required=True),
        "code": fields.char("Code", size=64, required=True),
        "max_amount": fields.float("Max Amount", required=True),
        "account_id": fields.many2one("account.account","Account", required=True),
        "balance": fields.function(_balance,method=True,type="float",string="Current Balance"),
        "notes": fields.text("Notes"),
        "moves": fields.one2many("account.cash.move","fund_id","Cash Moves"),
        'active': fields.boolean('Active'),
        'company_id': fields.many2one('res.company','Company', required=1),
    }

    _defaults={
        'active': True,
        "company_id": lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
        }
    
account_petty_fund()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
