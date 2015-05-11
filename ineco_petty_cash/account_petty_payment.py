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

class account_petty_payment(osv.osv):
    _name = "account.petty.payment"

    STATES = [('draft', 'Draft'), ('posted', 'Posted'), ('canceled', 'Canceled')]
    REQUIRED = {'required': True, 'readonly': True, 'states': {'draft': [('readonly', False)]}}
    OPTIONAL = {'required': False, 'readonly': True, 'states': {'draft': [('readonly', False)]}}

    def _amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        for petty in self.browse(cr,uid,ids, context=context):
            res[petty.id] = { 'amount_untaxed': 0.0
                               , 'amount_tax': 0.0
                               , 'amount_total': 0.0
                               }

            for vat in petty.vat_lines:
                res[petty.id]['amount_tax'] += vat.tax_amount

            for line in petty.lines:
                res[petty.id]['amount_total'] += line.subtotal
                res[petty.id]['amount_untaxed'] += line.subtotal_excl

        return res

    def _pay_amount(self,cr,uid,ids,name,args,context=None):
        vals={}
        for petty in self.browse(cr,uid,ids):
            amount_inv=petty.amount_total
            amount_wht=0.0
            #for wht in petty.wht_lines:
            #    amount_wht+=wht.tax_amount
            vals[petty.id]={
                "amount_inv": amount_inv,
                "amount_wht": amount_wht,
                "amount_to_pay": amount_inv-amount_wht,
            }
        return vals

    _columns={
        "name": fields.char("Doc No",size=64,required=True,readonly=True,select=1),
        "date": fields.date("Doc Date", select=1, **REQUIRED),
        "fund_id": fields.many2one("account.petty.fund","Petty Cash Fund", **REQUIRED),
        "employee_id": fields.many2one("res.users", "Employee", **REQUIRED),
        "desc": fields.char("Description", size=128, **OPTIONAL),
        "lines": fields.one2many("account.petty.payment.line", "petty_id", "Lines", **OPTIONAL),
        "notes": fields.text("Notes", **OPTIONAL),
        "state": fields.selection(STATES, "Status", readonly=True),
        "paid_total" : fields.float('Paid Total',digits_compute=dp.get_precision('Account'), **REQUIRED),#require in view
        "amount_untaxed": fields.function(_amount,method=True,type="float",string="Untaxed Amount",multi="amount"),
        "amount_tax": fields.function(_amount,method=True,type="float",string="Tax",multi="amount"),
        "amount_total": fields.function(_amount,method=True,type="float",string="Total Amount",multi="amount"),
        "amount_inv": fields.function(_pay_amount,method=True,type="float",string="Invoice Total",multi="pay_amount"),
        "amount_wht": fields.function(_pay_amount,method=True,type="float",string="Withholding Tax",multi="pay_amount"),
        "amount_to_pay": fields.function(_pay_amount,method=True,type="float",string="Amount To Pay",multi="pay_amount"),
        "company_id": fields.many2one("res.company", "Company", **REQUIRED),
        "journal_id": fields.many2one("account.journal", "Journal", **REQUIRED),
        "move_id": fields.many2one("account.move", "Journal Entry", readonly=True),
        "vat_lines": fields.one2many("account.tax.line", "petty_id", "VAT Lines"),
        #"wht_lines": one2many_dom("account.tax.line", "petty_id", "WHT Lines", domain=[('tax_id.tax_group','=','wht')], **OPTIONAL),
        "cash_moves": fields.one2many("account.cash.move", "petty_id", "Cash Moves", **OPTIONAL),
    }

    def _get_journal(self,cr,uid,context):
        res = self.pool.get('account.journal').get_account_journal(cr,uid,'account.petty.payment',context=context)
        return res

    _defaults={
        "journal_id":_get_journal,
        "name": lambda *a: "/",
        "state": lambda *a: "draft",
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "company_id":lambda self,cr,uid,context: self.pool.get('res.company').get_company(cr,uid,context).id,
    }

    def onchange_company_id(self, cr, uid, ids,company_id):
        journal_id = self._get_journal(cr,uid,context={'company_id':company_id})
        vals={}
        vals["journal_id"]= journal_id
        return {"value":vals}

    def create(self,cr,uid,vals,context={}):
        company_id = vals.get('company_id',False)
        context.update({'company_id':company_id,'process_date':vals.get('date',time.strftime('%Y-%m-%d'))})
        if not "name" in vals or vals["name"]=="/":
            vals["name"]=self.pool.get("ir.sequence").get(cr,uid,"ineco.petty.payment",context=context)
        return super(account_petty_payment,self).create(cr,uid,vals,context)

    def btn_compute_taxes(self,cr,uid,ids,context=None):
        tax_line_obj = self.pool.get('account.tax.line')
        for petty in self.browse(cr,uid,ids):
            cr.execute("DELETE FROM account_tax_line WHERE petty_id=%s", (petty.id,))
            res=tax_line_obj.compute(cr, uid, petty.id, type="petty", context=context).values()
            for vals in res:
                tax_line_obj.create(cr, uid, vals)
        return True

    def button_post(self,cr,uid,ids,context=None):
        ml_obj=self.pool.get('account.move.line')

        for petty in self.browse(cr,uid,ids):
            petty.btn_compute_taxes()
            company_id = petty.company_id.id
            if petty.amount_to_pay > petty.fund_id.max_amount:
                raise osv.except_osv(_('Error'), _('This Payment exceeds the maximum authorised Amount'))

            if petty.amount_to_pay > petty.fund_id.balance:
                raise osv.except_osv(_('Error'), _('This Payment exceeds the current Balance of the Petty Cash Fund'))

            context.update({'company_id':company_id})

            # find accounting period
            period_id = self.pool.get('account.period').\
                find(cr,uid,dt=petty.date,context=context)[0]


            lref=petty.name
            # create cash move
            cash_move_vals={
                "petty_id": petty.id,
                "fund_id": petty.fund_id.id,
                "amount": petty.amount_to_pay,
                "account_id":petty.fund_id.account_id.id,
                "type": "out",
                "date": petty.date,
                "name": lref,
            }
            
            cashmove_obj =  self.pool.get('account.cash.move')
            cashmove_obj.create(cr, uid, cash_move_vals, context)

            vals={
                "ref": lref,
                'notes': _('Petty Cash Payment ') + petty.employee_id.name,
                "journal_id": petty.journal_id.id,
                "period_id": period_id,
                "date": petty.date,
                "vat_lines": [(4,vat.id) for vat in petty.vat_lines],
                #"wht_lines": [(4,wht.id) for wht in petty.wht_lines],
                "cash_moves": [(0,0,cash_move_vals)],
                'company_id':company_id,
            }
            
            move_id=self.pool.get("account.move").create(cr,uid,vals)
            lines=[]

            # make entries in expense accounts
            for line in petty.lines:
                vals={
                    "account_id": line.account_id.id,
                    "debit": line.subtotal_excl > 0.0 and line.subtotal_excl or 0.0,
                    "credit": line.subtotal_excl < 0.0 and abs(line.subtotal_excl) or 0.0,
                    "name": _('Petty Cash Payment ') + petty.employee_id.name,
                    "date": petty.date,
                    "ref": lref,
                }
                lines.append(vals)

            # make entries in tax accounts
            for vat in petty.vat_lines:
                vals={
                    "account_id": vat.account_id.id,
                    "debit": vat.tax_amount,
                    "credit": 0.0,
                    "name": _('Petty Cash Payment ') + petty.employee_id.name,
                    "date": vat.date,
                    "ref": lref,
                }
                lines.append(vals)

            # make entry in petty cash account
            vals={
                "account_id": petty.fund_id.account_id.id,
                "debit": 0.0,
                "credit": petty.amount_to_pay,
                "name": petty.desc or _('Petty Cash Payment ') + petty.employee_id.name,
                "date": petty.date,
                "ref": lref,
            }
            lines.append(vals)

            # make entries in wht accounts
#             for wht in petty.wht_lines:
#                 vals={
#                     "move_id": move_id,
#                     "account_id": wht.account_id.id,
#                     "debit": 0.0,
#                     "credit": wht.tax_amount,
#                     "name": _('Petty Cash Payment ') + petty.employee_id.name,
#                     "date": wht.date,
#                     "ref": lref,
#                 }
#                 lines.append(vals)
            #lines.append(vals)

            #lines = ml_obj.group_move_lines(cr,uid,lines)
            for l in lines:
                l['move_id']=move_id
                ml_obj.create(cr,uid,l)

            petty.write({"move_id":move_id})
            #self.pool.get('account.move').action_process(cr,uid,move_id)
            self.pool.get('account.move').button_validate(cr, uid, [move_id])
            petty.write({"state":"posted"})
        return True

    def action_cancel(self,cr,uid,ids,context=None):
        for obj in self.browse(cr,uid,ids):
            for cm in obj.cash_moves:
                cm.action_cancel()
        self.write(cr,uid,ids,{"state":"canceled"})
        return True

    def button_cancel(self,cr,uid,ids,context=None):
        for obj in self.browse(cr,uid,ids):
            if obj.state=='canceled':
                continue
            move_obj=obj.move_id
            cr.execute("""
                delete from account_cash_move where petty_id = %s
            """ % (obj.id))
            if move_obj:
                if move_obj.state=='posted':
                    #move_obj.revert_move(cr,uid,[move.id])
                    move_obj.button_cancel()
                else:
                    #move_obj.action_reset(cr,uid,[move.id])
                    move_obj.button_cancel()

        self.action_cancel(cr,uid,ids,context)
        return True

    def button_draft(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{"state": "draft"})
        return True

    def unlink(self, cr, uid, ids, context=None):
        payments= self.read(cr, uid, ids, ['state'])
        unlink_ids = []
        for t in payments:
            if t['state'] in ('draft'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete payment(s) that are already posted!'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True
account_petty_payment()

class account_petty_payment_line(osv.osv):
    _name = "account.petty.payment.line"

    def _subtotal(self, cr, uid, ids, name, args, context=None):
        tax_obj = self.pool.get('account.tax')
        result = {}

        for line in self.browse(cr, uid, ids):
            subtotal = line.quantity * line.price_unit
            result[line.id] = {'subtotal': subtotal, 'subtotal_excl': subtotal}

            if line.taxes:
                tax_values = tax_obj.compute_all(cr, uid, line.taxes, line.price_unit, line.quantity, False, False, False)

                result[line.id]['subtotal'] = tax_values['total']
                result[line.id]['subtotal_excl'] = tax_values['total']

                for item in tax_values['taxes']:
                    result[line.id]['subtotal'] += item['amount']

        return result

    _columns={
        "petty_id": fields.many2one("account.petty.payment","Payment",ondelete="cascade"),
        "product_id": fields.many2one("product.product","Product"),
        "name": fields.char("Description",size=64,required=True),
        "account_id": fields.many2one("account.account","Account",required=True),
        "price_unit": fields.float("Unit Price",required=True),
        "quantity": fields.float("Quantity",required=True),
        "taxes": fields.many2many("account.tax","petty_payment_tax","line_id","tax_id","Taxes"),
        "subtotal": fields.function(_subtotal, method=True, type="float", string="Subtotal", multi='taxes'),
        "subtotal_excl": fields.function(_subtotal, method=True, type="float", string="Subtotal (Tax excl.)", multi='taxes'),
        "invoice_no": fields.char('Invoice No', size=64, select=1),
        "date": fields.date("Date", select=1),
        "partner_id": fields.many2one("res.partner","Partner"),
        "tax_period_id": fields.many2one("account.period","Tax Period",select=1),
    }

    def default_get(self,cr,uid,fields,context=None):
        vals=super(account_petty_payment_line,self).default_get(cr,uid,fields,context)

        if 'quantity' in fields:
            vals['quantity']=context.get('quantity',1.0)

        if 'price_unit' in fields:
            vals['price_unit']=context.get('amount',0.0)
        return vals

    #TODO: make sure it work for multi company
    def onchange_product(self,cr,uid,ids,product_id):
        if not product_id:
            return {}
        prod=self.pool.get("product.product").browse(cr,uid,product_id)
        vals={
            "name": prod.name,
            "account_id": prod.product_tmpl_id.property_account_expense.id or prod.categ_id.property_account_expense_categ.id,
            "price_unit": prod.standard_price,
            "quantity": 1,
            "taxes": [t.id for t in prod.supplier_taxes_id],
        }
        return {"value": vals}
account_petty_payment_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
