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

class account_cash_move(osv.osv):
    _name="account.cash.move"
    _order="date,id"
    _CONTROL={"draft":[("readonly",False)]}

    def _dep_wit(self,cr,uid,ids,name,arg,context=None):
        vals={}
        for cm in self.browse(cr,uid,ids):
            vals[cm.id]={
                "deposit": cm.type=="in" and cm.amount or 0.0,
                "withdraw": cm.type=="out" and cm.amount or 0.0,
            }
        return vals

    def get_extra_cause(self,cr,uid,data):
        """ support to add extra function that need to added in balance query
        """
        cause= ''
        params = ()
        return {'cause':cause,'params':params}

    def _balance(self,cr,uid,ids,name,arg,context=None):
        fund_id=context.get("fund_id",False)
        #if not fund_id:
            #raise osv.except_osv(_("Error"),_("Failed to compute balance, missing petty cash fund in context"))
        date_from=context.get("date_from",time.strftime('%Y-01-01'))
        vals = {}
        bal = 0.0

        extra_cause = self.get_extra_cause(cr,uid,context)

        for o in self.browse(cr, uid, ids):
            fund_id=context.get("fund_id",o.fund_id.id)
            if not date_from and not fund_id:
                bal=0.0
            else:
                # 1. get amount of prior date
                # 2. get amount of current date with lower id
                cr.execute("""
                    select sum(c.amount) from (
                        (
                        SELECT sum(CASE WHEN TYPE = 'in' THEN amount ELSE -amount END) as amount
                        FROM account_cash_move
                        WHERE fund_id = %s
                          AND date < %s)
                    UNION
                        (
                        SELECT sum(CASE WHEN TYPE = 'in' THEN amount ELSE -amount END) as amount
                        FROM account_cash_move
                        WHERE fund_id = %s
                          AND date = %s and id<%s)
                    ) c
                                """+extra_cause['cause']
                                ,(fund_id,o.date,fund_id,o.date,o.id,)+extra_cause['params'])
                res=cr.fetchone()
                bal=res[0] or 0.0

            if fund_id and (o.fund_id.id!=fund_id):
                raise osv.except_osv(_("Error"),_("Failed to compute balance, wrong petty cash fund"))
            bal+=o.type=="in" and o.amount or -o.amount
            vals[o.id]=bal
        return vals

    def _get_amount_word(self,cr,uid,ids,name,arg,context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            result[obj.id] = num2word(obj.amount,l=context.get('lang','th_TH'))
        return result

    _columns={
        "name": fields.char("Doc No.",size=64,readonly=1,states=_CONTROL,select=1),
        "invoice_id": fields.many2one("account.invoice","Invoice",ondelete="cascade", select=1),
        #"payment_id": fields.many2one("account.payment","Payment",ondelete="cascade"),
        #"advance_id": fields.many2one("account.advance","Advance",ondelete="cascade"),
        #"advance_clear_id": fields.many2one("account.advance.clear","Advance Clearing",ondelete="cascade"),
        "petty_id": fields.many2one("account.petty.payment","Petty Cash Payment",ondelete="cascade"),
        "move_id": fields.many2one("account.move","Journal Entry",readonly=1),
        "amount": fields.float("Amount",required=True,readonly=1,states=_CONTROL),
        "type": fields.selection([("in","In"),("out","Out")],"Type",required=True,change_default=True),
        "fund_id": fields.many2one("account.petty.fund","Petty Cash Fund",change_default=True,readonly=1,states=_CONTROL,select=1),
        "notes": fields.text("Notes"),
        "account_id": fields.many2one("account.account","Account",required=True,readonly=1,states=_CONTROL),
        "other_account_id": fields.many2one("account.account","Other Account",states=_CONTROL),
        "date": fields.date("Date",readonly=1,states=_CONTROL),
        "state": fields.selection([("draft","Draft"),("posted","Posted"),("canceled","Canceled")],"Status",readonly=True,select=1),
        "journal_id": fields.many2one("account.journal","Journal",readonly=True,states=_CONTROL),
        "deposit": fields.function(_dep_wit,method=True,type="float",string="Deposit",multi="dep_wit"),
        "withdraw": fields.function(_dep_wit,method=True,type="float",string="Withdraw",multi="dep_wit"),
        "balance": fields.function(_balance,method=True,type="float",string="Balance"),
        "analytic_account_id" : fields.many2one("account.analytic.account","Analytic Account",readonly=1,states=_CONTROL),
        "amount_word": fields.function(_get_amount_word,method=True,type="string",string="Amount Word"),
        "company_id": fields.many2one('res.company','Company',required=1,readonly=1,states=_CONTROL,select=1),
        "description": fields.related("move_id","move_name_ref",type="char",readonly=True,string="Description"),
    }

    def _get_cash_account(self,cr,uid,context):
        #cash = False
        company_obj = self.pool.get('res.company')
        company_ids = company_obj._company_default_get(cr, uid, 'account.account', context=context)
        cash = company_obj.browse(cr, uid, company_ids).cash
        res = cash and cash.id or False
        return res

    def _get_journal(self,cr,uid,context):
        #res = self.pool.get('account.journal').get_account_journal(cr,uid,'account.cash.move',context=context)
        res = False
        return res

    def _get_type(self,cr,uid,context):
        return context.get('type',False)

    _defaults={
        "name": lambda self,cr,uid,context: context.get("name","/"),
        "state": lambda *a: "draft",
        "amount": lambda self,cr,uid,context: context.get("amount",False),
        "type": _get_type,
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "company_id": lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
        "journal_id":_get_journal,
        "account_id" : _get_cash_account,
    }

    def onchange_company_id(self, cr, uid, ids, company_id,type):
        context={'company_id':company_id,'type':type}
        journal_id = self._get_journal(cr,uid,context=context)
        account_id= self._get_journal(cr,uid,context=context)
        vals={}
        vals["journal_id"]= journal_id
        vals["account_id"]= account_id
        return {"value":vals}

    def default_get(self,cr,uid,fields,context=None):
        vals=super(account_cash_move,self).default_get(cr,uid,fields,context)
        res=self.pool.get("ir.values").get(cr,uid,"default","type=%s"%context.get("type"),[self._name])
        for id,field,value in res:
            if field in fields:
                vals[field]=value

        return vals

    def create(self,cr,uid,vals,context=None):
        company_id=vals.get('company_id',False)
        context.update({'company_id':company_id,'process_date':vals.get('date',time.strftime('%Y-%m-%d'))})

        if not "name" in vals or vals["name"]=="/":
            vals["name"]=self.pool.get("ir.sequence").get(cr,uid,"petty.received",context=context)
        return super(account_cash_move,self).create(cr,uid,vals,context)

    def onchange_fund(self,cr,uid,ids,fund_id):
        if not fund_id:
            return {}
        fund=self.pool.get("account.petty.fund").browse(cr,uid,fund_id)
        vals={
            "account_id": fund.account_id.id,
        }
        return {"value":vals}

    def move_line_get(self, cr, uid, invoice_id):
        res = []
        inv = self.pool.get("account.invoice").browse(cr,uid,invoice_id) if type(invoice_id) in (int, long) else invoice_id
        for cm in inv.cash_moves:
            res.append({
                'type':'cash',
                'name': inv.name or inv.name_ext,
                'price_unit': cm.amount,
                'quantity': 1,
                'price': cm.amount or 0.0,
                'account_id': cm.account_id.id,
            })
        return res

    def button_post(self,cr,uid,ids,context=None):
        for cm in self.browse(cr,uid,ids):
            company_id=cm.company_id.id
            context.update({'company_id':company_id})

            # find accounting period
            period_id = self.pool.get('account.period').\
                find(cr,uid,dt=cm.date,context=context)[0]

            if not cm.fund_id:
                raise osv.except_osv(_("Error"),_("Missing petty cash fund"))
            if not cm.journal_id:
                raise osv.except_osv(_("Error"),_("Missing journal"))
            if not cm.account_id or not cm.other_account_id:
                raise osv.except_osv(_("Error"),_("Missing account"))
            vals={
                "journal_id": cm.journal_id.id,
                "period_id": period_id,
                "date": cm.date,
                "ref":cm.name,
                'company_id':company_id,
            }
            move_id=self.pool.get("account.move").create(cr,uid,vals)
            name=_('Petty Cash Receive')

            # make entry in petty cash account
            vals={
                "move_id": move_id,
                "account_id": cm.account_id.id,
                "debit": cm.amount,
                "credit": 0.0,
                "name": name,
                "date": cm.date,
            }
            self.pool.get("account.move.line").create(cr,uid,vals)

            # make entry in other account
            vals={
                "move_id": move_id,
                "account_id": cm.other_account_id.id,
                "debit": 0.0,
                "credit": cm.amount,
                "name": name,
                "date": cm.date,
            }
            self.pool.get("account.move.line").create(cr,uid,vals)
            cm.write({"move_id": move_id})
            #self.pool.get("account.move").action_process(cr,uid,move_id)
            self.pool.get('account.move').button_validate(cr, uid, [move_id])

            cm.write({"state":"posted"})
        return True

    def action_cancel(self,cr,uid,ids,context=None):
        for obj in self.browse(cr,uid,ids,context):
            obj.write({"state": "canceled"})
        return True

    def button_cancel(self,cr,uid,ids,context=None):
        move_obj = self.pool.get("account.move")
        for obj in self.browse(cr,uid,ids,context):
            if obj.state=='canceled':
                continue
            move=obj.move_id
            if move:
                if move.state=='posted':
                    #move_obj.revert_move(cr,uid,[move.id])
                    move_obj.button_cancel(cr, uid, [move.id])
                else:
                    #move_obj.action_reset(cr,uid,[move.id])
                    move_obj.button_cancel(cr, uid, [move.id])
        self.action_cancel(cr,uid,ids,context)
        return True

    def button_draft(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state": "draft"})
        return True

    #def unlink(self, cr, uid, ids, context=None):
        #cm= self.read(cr, uid, ids, ['state'])
        #unlink_ids = []
        #for t in cm:
            #if t['state'] in ('draft'):
                #unlink_ids.append(t['id'])
            #else:
                #raise osv.except_osv(_('Invalid action !'), _('Cannot delete entries that are already posted!'))
        #osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        #return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='tree', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        # NOTE : for print screen it's call fields_view_get if we need to show view of the current screen 
        # Need to overwrite
        if view_type=='tree':
            view_id=context.get('view_id',None)
            result = super(account_cash_move, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        else:
            result = super(account_cash_move, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        return result

account_cash_move()

