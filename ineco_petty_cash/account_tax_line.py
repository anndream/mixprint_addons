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
from tools.translate import _
#from pprint import pprint
#from ac_utils import dec #compute by decimal accuracy

class account_tax_line(osv.osv):
    _name="account.tax.line"

    def _name_ext(self, cr, uid, ids, field_name, arg, context):
        if not context:
            context={}
        res={}
        for obj in self.browse(cr, uid, ids):
            doc_no=''

            if obj.payment_id:
                doc_no = obj.payment_id.name
            elif obj.petty_id:
                doc_no = obj.petty_id.name
            elif obj.bank_move_id:
                doc_no = obj.bank_move_id.name
            elif obj.cheque_move_id:
                doc_no = obj.cheque_move_id.name
            elif obj.advance_clear_id:
                doc_no = obj.advance_clear_id.name
            else:
                doc_no='/'

            res[obj.id]=doc_no
        return res

    #TODO : Think about offset tax if we need to allow 1 payment and select custoer,supplier invoice
    _columns={
        "invoice_id": fields.many2one("account.invoice","Invoice",ondelete="cascade",select=1,readonly=1),
        #"payment_id": fields.many2one("account.payment","Payment",ondelete="cascade",readonly=1,select=1),
        "petty_id": fields.many2one("account.petty.payment","Petty Cash Payment",ondelete="cascade",readonly=1,),
        #"advance_clear_id": fields.many2one("account.advance.clear","Advance Clearing",ondelete="cascade",readonly=1),
        "move_id": fields.many2one("account.move","Journal Entry",readonly=1),
        #"cheque_move_id": fields.many2one("account.cheque.move","Cheque Transaction",readonly=1,ondelete="cascade",select=1),
        #"bank_move_id": fields.many2one("account.bank.move","Bank Transaction",readonly=1,ondelete="cascade"),
        "tax_id": fields.many2one("account.tax","Tax",required=True,select=1),
        #"tax_group": fields.related("tax_id","tax_group",type="char",size=32,string="Tax Group",store=True,select=1),
        "period_id": fields.many2one("account.period","Period",select=1),
        "name": fields.char("Description",size=64),
        "base_amount": fields.float("Base Amount",required=True,digits=(16,2)), #TODO: decimal precision
        "tax_amount": fields.float("Tax Amount",required=True,digits=(16,2)),
        "ref": fields.char("Reference",size=64,select=1),
        "date": fields.date("Date",required=True,select=1),
        "partner_id": fields.many2one("res.partner","Partner"),
        "partner_name": fields.char("Partner Name",size=64),
        "id_no": fields.char("ID No",size=64,help="Personal Identifiaction No"),
        "tax_id_no": fields.char("Tax ID No",size=64,help="Taxpayer Identification no"),
        #"wht_type": fields.selection([("pnd53","Company"),("pnd3","Personal")],"WHT Type"),
        #"wht_payee": fields.selection([("once","Pay tax once"),("always","Pay tax always"),("wht","Withholding Tax"),("other","Other")],"Payee"),
        #"wht_payee_other": fields.char("Payee Other",size=64),
        #"wht_filing_type": fields.selection([("ord","Ordinary Filing"),("add","Additional Filing")],"Filing Type"),
        #"wht_filing_times": fields.integer("Filing Times"),
        "account_id": fields.many2one("account.account","Account",required=True,select=1),
        #"assessable_type": fields.selection(
        #    [ ("40_1",  "Section 40(1)")
        #    , ("40_2",  "Section 40(2)")
        #    , ("40_3",  "Section 40(3)")
        #    , ("40_4a", "Section 40(4)(a)")
        #    , ("40_4b_1.1", "Section 40(4)(b_1.1)")
        #    , ("40_4b_1.2", "Section 40(4)(b_1.2)")
        #    , ("40_4b_1.3", "Section 40(4)(b_1.3)")
        #    , ("40_4b_1.4", "Section 40(4)(b_1.4)")
        #    , ("40_4b_2.1", "Section 40(4)(b_2.1)")
        #    , ("40_4b_2.2", "Section 40(4)(b_2.2)")
        #    , ("40_4b_2.3", "Section 40(4)(b_2.3)")
        #    , ("40_4b_2.4", "Section 40(4)(b_2.4)")
        #    , ("40_4b_2.5", "Section 40(4)(b_2.5)")
        #    , ("section_3", "Section 3 Quattuordecim")
        #    , ("other", "Other(Note)")
        #    ], "Assessable Type"),#for whithholding tax report
        'type_tax_use': fields.selection([('sale','Sale'),('purchase','Purchase')], 'Tax Application', required=True),
        "company_id" : fields.many2one('res.company','Company',required=1),
        "state": fields.selection([('open','Open'),('canceled','Canceled'),('done','Done')],string="State",readonly=1),

        # Use in report
        #"name_ext": fields.function(_name_ext,method=True,type="char",size="64",string="Doc No"),
    }
    _order="date,id"

    #def _check_move_id(self,cr,uid,ids,context=None):
        #print 'check_move_id',ids
        #for line in self.browse(cr,uid,ids,context):
            #if line.move_id:
                #if not line.ref:
                    #return False
        #return True
    #_constraints=[
        #(_check_move_id,'Missing WHT No',['move_id']),
    #]

    def _get_wht_type(self,cr,uid,context):
        partner_id = context.get('partner_id',False)
        res=False
        if partner_id:
            res = self.pool.get('res.partner').browse(cr,uid,partner_id).wht_type
        return res

    _defaults={
        'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
        'type_tax_use': lambda self,cr,uid,context : context.get('type_tax_use','purchase'),

        #'assessable_type':'other',
        #'wht_payee':'wht',
        #'wht_filing_type':'ord',
        "state" : 'open',
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res = super(account_tax_line, self).create(cr, uid, vals, context)
        return res

#     def write(self, cr, uid, ids, vals, context=None):
#         if context is None:
#             context = {}
# 
#         # Dont allow changing the company_id when account_move_line already exist
# 
#         if 'date' in vals:
#             tl = self.browse(cr,uid,ids)[0]
#             if tl.type_tax_use=='purchase' and tl.tax_group=='wht' and tl.date:
#                 if vals['date']!=tl.date:
#                     #raise osv.except_osv(_('Warning !'), _('You cannot modify date of WHT'))
#                     raise osv.except_osv(_('Warning !'), _('ไม่สามารถแก้ไขวันที่ ัหก ณ ที่จ่าย ได้'))
#         return super(account_tax_line, self).write(cr, uid, ids, vals, context=context)

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False,submenu=False):
        if not context:
            context = {}
        res = super(account_tax_line,self).fields_view_get(cr, uid, view_id, view_type, context, toolbar,submenu)

        fields=res.get('fields',{})
        if fields:
            if context.get('tax_group','')=='vat':
                if fields.get('ref'):
                    res['fields']['ref']['string'] = _('Invoice No')
            else:
                if fields.get('ref'):
                    res['fields']['ref']['string'] = _('WHT No')

        return res

    def get_tax_account(self,cr,uid,tax_id,company_id,partner_id=False,context={}):
        fpos_obj = self.pool.get('account.fiscal.position') #TODO: fiscal positin support
        #in==invoice
        #out==refund
        if not context:
            context={}
        if not company_id:
            company_id = self.pool.get('res.company').get_company(cr,uid,context).id
        context.update({'company_id':company_id})
        tax= self.pool.get('account.tax').browse(cr,uid,tax_id,context=context)
        property_obj = self.pool.get('ir.property')

        company= self.pool.get('res.company').browse(cr,uid,company_id)
        partner=False
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr,uid,partner_id,context=context)
        account_id = tax.account_collected_id.id or False
        #if tax.tax_group=='vat':
        #    account_id = tax.account_collected_id.id or False

        #WHT purchase dont care properties
        #if tax.tax_group=='wht':
        #    if tax.type_tax_use=='purchase':
        #        wht_type='pnd53'
        #        if partner and partner.wht_type:
        #            wht_type=partner.wht_type
        #        if partner_id and wht_type=='pnd53':
        #            account_id = company.wht_company_id and company.wht_company_id.id or False
        #        elif partner_id and wht_type=='pnd3':
        #            account_id = company.wht_personal_id and company.wht_personal_id.id or False
        #        else:
        #            account_id = tax.account_collected_id.id or False
        #            #account_id = property_obj.get_property(cr,uid,'account_collected_id','account.tax',res_id=tax.id,context=context) #use in multi company

        #    else:
        #        account_id = tax.account_collected_id.id or False
                #account_id = property_obj.get_property(cr,uid,'account_collected_id','account.tax',res_id=tax.id,context=context) #use in multi company

        if not account_id:
            #print 'Config Error'
            #print 'tax_id',tax_id,tax.tax_group,tax.type_tax_use
            #print 'company_id',company_id
            #print 'partner_id',partner_id
            #print 'context',context
            #raise osv.except_osv(_("Configuration Error"),_("Account of Tax missing"))
            raise osv.except_osv(_("Configuration Error"),_("Account of Tax missing"))

        return account_id

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        #default.update({'state':'draft', 'number':False, 'move_id':False, 'move_name':False,})
        #if 'date_invoice' not in default:
            #default['date_invoice'] = False
        #if 'date_due' not in default:
            #default['date_due'] = False
        return super(account_tax_line, self).copy(cr, uid, id, default, context)

    def default_get(self,cr,uid,fields,context=None):
        if not context:
            context={}
        vals=super(account_tax_line,self).default_get(cr,uid,fields,context)
        if context.get("ref"):
            vals["ref"]=context["ref"]
        if context.get("date"):
            vals["date"]=context["date"]
        if context.get("partner_id"):
            partner=self.pool.get("res.partner").browse(cr,uid,context["partner_id"])
            vals.update({
                "partner_id": partner.id,
                "partner_name": partner.name,
                "tax_id_no": partner.tin,
                "id_no": partner.tin,
            })
        if 'wht_type' in fields:
            vals['wht_type']= self._get_wht_type(cr,uid,context)

        return vals

    #NOTE:  Some project need to modify this function
    #       to fill tax reference
    def get_tax_ref(self,cr,uid,model,obj_browse):
        """
            @params model :orm model
            @params obj_browse: browse record of model

            @return :Tax line reference
        """

        ref =''
        if model=='account.invoice':
            if obj_browse.type in ("out_invoice","out_refund","out_deposit","out_cash"):
                ref=obj_browse.internal_number
            else:
                ref=obj_browse.reference

        #XXX: this no need to put because it need to get from tax invoice
        # now account_thai have no place to record tax invoice
        elif model=='account.payment':
            pass

        elif model=='account.tax.line':
            ref = obj_browse.ref

        return ref

    #split to specific function becuase this might be difference
    #Bussiness
    def get_tax_partner(self,cr,uid,partner,invoice=False):
        if invoice:
            partner = invoice.partner_id
        return ( partner.id, partner.complete_name)

    #Overwrite to other project
    def _payment_check_vat(self,cr,uid,pml):
        return False

    def invoice_get_date(self,cr,uid,inv):
        date = inv.date_invoice or time.strftime("%Y-%m-%d")
        if inv.type.startswith('out_'):
            date = inv.doc_date or time.strftime("%Y-%m-%d")
        return date

    def compute_tax_payment(self,cr,uid,obj_id,context=None):
        tax_obj = self.pool.get('account.tax')
        tax_lines=[]
        pmt = self.pool.get("account.payment").browse(cr, uid, obj_id, context)
        cur = pmt.currency_id
        for pmt_line in pmt.lines:
            if not pmt_line.invoice_id:
                continue

            #check payment suspended vat 
            #sometime it already create in account move
            vat_suspend = self._payment_check_vat(cr,uid,pmt_line)
            if vat_suspend:
                continue

            inv=pmt_line.invoice_id
            ratio = inv.amount_total and (pmt_line.amount/inv.amount_total) or 1 #division by Zero error

            partner_id,partner_name = self.get_tax_partner(cr,uid,pmt.partner_id,inv)

            #Group lines and tax by 1 payment
            groups = {}
            lines=[]

            for line in inv.invoice_line:
                line_invoice_line_tax_id = list(set(line.invoice_line_tax_id))

                for cnt,l in enumerate(line_invoice_line_tax_id):

                    #If vat is not amortized vat it will be skipped
                    if not l.amortized_tax_id:
                        continue

                    groups.setdefault(l,[]).append(line)

            for tax,invoice_lines in groups.items():

                #NOTE : We need to change this , not compute tax based on  tax config
                #Should use base on document  same as V5


                base_amount=0.0
                #Use decimal
                if tax.tax_group=='vat':
                    base_amount = float(sum([ dec(line.base_amount) - dec(line.discount_extra_amount) for line in invoice_lines]))
                else:
                    base_amount = float(sum([ dec(line.price_subtotal_extra) for line in invoice_lines]))

                #FIXME: Now if compute wht need to compute from amount_untaxed


                #This will return wht and vat(amortized_id)
                #Price belong to type of VAT(Inc/Exc)
                tax_vals=tax_obj.compute_all(cr, uid, [tax], base_amount, 1, inv.address_invoice_id.id,\
                        line.product_id, inv.partner_id, no_wht=False, no_vat=False,amortized_ok=True)

                #print tax_vals
                lines+=tax_vals['taxes']


            for tax in lines:
                #NOTE: In account thai we don't care about collected/paid account we can use onley collected account
                account_id = self.get_tax_account(cr,uid,tax['id'],inv.company_id.id,inv.partner_id.id,context=context) or False

                val={}
                val['payment_id'] = pmt.id
                val['tax_id']=tax['id']
                val['name'] = tax['usage']
                val['tax_amount'] = tax['amount']
                val['base_amount'] = tax['price_unit']
                val['date']=pmt.date or time.strftime('%Y-%m-%d')
                val["partner_id"]=partner_id
                val["partner_name"]=partner_name
                val["tax_id_no"]=pmt.partner_id.tin #TODO: Use only 1 field for tax_id
                val["id_no"]=pmt.partner_id.tin
                #val["tax_group"]=tax['tax_group']
                val["account_id"] = account_id

#                 if tax['tax_group']=="wht":
#                     val["wht_payee"]="wht"
#                     val["group_key"]=partner_id

                #elif tax['tax_group']=='vat':
                val['ref']= self.get_tax_ref(cr,uid,'account.payment',pmt)
                #apply this group for VAT
                val["group_key"]= inv and inv.id or False

                val["base_amount"]*=ratio
                val["tax_amount"]*=ratio

                tax_lines.append(val)
        return tax_lines

    def compute(self, cr, uid, obj_id, type="invoice", context=None):
        if not context:
            context = {}
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        tax_lines=[]
        cur=False

        if type=="invoice":
            inv = self.pool.get("account.invoice").browse(cr, uid, obj_id, context)
            #FIXME : invoice tax amount for other currency is it posxible ?
            cur = inv.currency_id
            tax_data={}
            invoice_tax_date = self.invoice_get_date(cr,uid,inv)

            #Sign for tax amount
            sign= inv.type in ('out_refund','in_refund')  and -1 or 1
            for line in inv.invoice_line:
                no_wht=inv.type not in ('out_cash','in_cash','out_deposit','in_deposit')

                line_invoice_line_tax_id=(set(line.invoice_line_tax_id))

                #price_unit = (line.price_unit * line.quantity) - line.discount_amount - line.discount_extra_amount
                price_unit = line.base_amount - line.discount_extra_amount
                if not price_unit:
                    continue
                tax_data.setdefault(tuple(line_invoice_line_tax_id),[]).append(price_unit)

            for k,v in tax_data.items():
                price_unit = sum(v)
                taxes = list(k)
                tax_vals=tax_obj.compute_all(cr, uid, taxes ,price_unit ,1,\
                    line.product_id, inv.partner_id, no_wht=no_wht)

                for tax in tax_vals['taxes']:
                    val={}
                    val['invoice_id'] = inv.id
                    val['tax_id']=tax['id']
                    val['name'] = tax['usage']
                    val['tax_amount'] = tax['amount'] * sign
                    val['base_amount'] = tax['price_unit'] * sign # quantity don't need to use because price_unit already included
                    val["date"]=invoice_tax_date
                    #val["tax_group"]=tax['tax_group']
                    val["ref"]=tax['tax_group']=='vat' and self.get_tax_ref(cr,uid,'account.invoice',inv) or False

                    val["partner_id"]=inv.partner_id.id
                    val["partner_name"]=inv.partner_id.name
                    val["tax_id_no"]=inv.partner_id.tin
                    val["id_no"]=inv.partner_id.tin

                    if inv.type in ('out_invoice','in_invoice','out_cash','in_cash','out_deposit','in_deposit'):
                        val['account_id'] = self.get_tax_account(cr,uid,tax['id'],inv.company_id.id,inv.partner_id.id,context=context) or line.account_id.id
                    else:
                        #now refund account use the same
                        val['account_id'] = self.get_tax_account(cr,uid,tax['id'],inv.company_id.id,inv.partner_id.id,context=context) or line.account_id.id

                    tax_lines.append(val)

            #DEPOSIT
            #XXX: should support tax in/excluded
            for line in inv.inv_deposit_lines:
                dep=line.deposit_id
                #proportional distribute base on amount
                rate= dep.amount_untaxed and line.amount/dep.amount_untaxed or 0.0 
                for tax in dep.vat_lines:
                    val={
                        "tax_id": tax.tax_id.id,
                        "base_amount": -tax.base_amount*rate,
                        "tax_amount": -tax.tax_amount*rate,
                        "invoice_id": inv.id,
                        "name": tax.name,
                        "date": tax.date,
                        "ref": self.get_tax_ref(cr,uid,'account.tax.line',tax),
                        "partner_id": tax.partner_id.id,
                        "partner_name": tax.partner_name,
                        "tax_id_no": tax.tax_id_no,
                        "id_no": tax.id_no,
                        'account_id': tax.account_id.id,
                        "tax_group" :tax['tax_group']
                    }

                    tax_lines.append(val)
        elif type=="payment":

            tax_lines+= self.compute_tax_payment(cr,uid,obj_id,context)

        elif type=="petty":
            #TODO :check discount func
            #TODO : support analytic,department
            petty = self.pool.get("account.petty.payment").browse(cr, uid, obj_id, context)
            cur = petty.company_id.currency_id
            for line in petty.lines:
                line_taxes=list(set(line.taxes))

                tax_vals = tax_obj.compute_all(cr, uid, line_taxes, line.price_unit, line.quantity, product=line.product_id)

                for tax in tax_vals['taxes']:
                    val={}
                    val['petty_id'] = petty.id
                    val['tax_id']=tax['id']
                    #val['name'] = tax['usage']
                    val['tax_amount'] = tax['amount']
                    val['base_amount'] = tax['price_unit'] * line['quantity']
                    val["date"]=petty.date
                    #if tax['tax_group']=="wht":
                    #    val["wht_payee"]="wht"

                    #val["tax_group"]=tax['tax_group']
                    #val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_id'] = self.get_tax_account(cr,uid,tax['id'],petty.company_id.id,context=context) or line.account_id.id
                    tax_lines.append(val)

        elif type=="advance_clear":
            #TODO : support analytic,department
            obj = self.pool.get("account.advance.clear").browse(cr, uid, obj_id, context)
            cur = obj.company_id.currency_id
            for line in obj.lines:
                line_taxes=list(set(line.taxes))#remove duplicate tax(web error)

                tax_vals = tax_obj.compute_all(cr, uid, line_taxes, line.amount, 1.0, product=line.product_id, no_wht=False)

                for tax in tax_vals['taxes']:
                    val={}
                    val['advance_clear_id'] = obj.id
                    val['tax_id']=tax['id']
                    val['name'] = tax['usage']
                    val['tax_amount'] = tax['amount']
                    val['base_amount'] = tax['price_unit']
                    val["date"]=obj.date
                    if tax['tax_group']=="wht":
                        val["wht_payee"]="wht"

                    val["tax_group"]=tax['tax_group']
                    if tax.get('account_collected_id', False):
                        val['account_id'] = tax['account_collected_id']
                    else:
                        val['account_id'] = line.account_id.id
                    tax_lines.append(val)

        tax_grouped = self.group_lines(cr,uid,tax_lines,cur)
        return tax_grouped

    def group_lines(self,cr,uid,lines,cur,context=None):
        tax_grouped={}
        for val in lines:
            #wht group , VAT group by invoice_id
            optional_group_key = ()

            if val.get('group_key',False):
                optional_group_key = (val['group_key'])

            key = (val['tax_id'],optional_group_key)

            if not key in tax_grouped:
                tax_grouped[key] = val
            else:
                tax_grouped[key]['base_amount'] += val['base_amount']
                tax_grouped[key]['tax_amount'] += val['tax_amount']
        """
        for t in tax_grouped.values():
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        """

        tax_grouped = self._finalize(cr,uid,tax_grouped,context)

        return tax_grouped

    def _finalize(self,cr,uid,tax_grouped,context=None):
        """ finalized tax line"""
        for key in tax_grouped.keys():
            #remove when tax ambount is 0
            if not tax_grouped[key]['base_amount']:
                del tax_grouped[key]
                continue #<<<

            tax = self.pool.get('account.tax').browse(cr,uid,key[0])
            rate = tax.amount
            base_amount=tax_grouped[key]['base_amount']
            tax_amount=tax_grouped[key]['tax_amount']
            #recheck tax amount is corrected or not
            computed_amount=round(base_amount*rate,2)
            if computed_amount!=round(tax_amount,2):
                tax_grouped[key]['tax_amount']=computed_amount

        return tax_grouped

    def get_invoice_move_lines_vat(self, cr, uid, invoice_id,context=None):
        inv = self.pool.get("account.invoice").browse(cr,uid,invoice_id) if type(invoice_id) in (int, long) else invoice_id
        group={}
        for vat in inv.vat_lines:
            #group vat line
            key=(vat.account_id.id)
            #key=(vat.account_id.id)
            group[key]=group.get(key,0.0)+(vat.tax_amount)
        res = []
        for (acc_id),amt in group.items():
        #for (acc_id),amt in group.items():
            #amount = 0 skip it
            if not amt:
                continue
            res.append({
                'type':'vat',
                'name': inv.name or inv.name_ext,
                'price_unit': abs(amt),
                'quantity': 1,
                'price': abs(amt),
                'account_id': acc_id,
            })
        return res

    def get_invoice_move_lines_wht(self, cr, uid, invoice_id):
        inv = self.pool.get("account.invoice").browse(cr,uid,invoice_id) if type(invoice_id) in (int, long) else invoice_id
        group={}
        for wht in inv.wht_lines:
            #group WHT
            if not wht.ref and wht.type_tax_use=='purchase' :
                raise osv.except_osv(_("Error"), _("WHT Doc No Missing"))
            key=(wht.account_id.id)
            group[key]=group.get(key,0.0)+wht.tax_amount
        res = []
        for (acc_id),amt in group.items():
            #amount = 0 skip it
            if not amt:
                continue
            res.append({
                'type':'wht',
                'name': inv.name or inv.name_ext,
                'price_unit': abs(amt),
                'quantity': 1,
                'price': abs(amt or 0.0),
                'account_id': acc_id,
            })
        return res

    def onchange_tax(self,cr,uid,ids,tax_id,base,partner_id=False,company_id=False):
        if not tax_id:
            return {}
        tax=self.pool.get("account.tax").browse(cr,uid,tax_id)
        account_id =self.get_tax_account(cr,uid,tax_id,company_id,partner_id)
        vals={
            "account_id":account_id,
            "name": tax.name,
            "tax_amount": 0.0,
            "type_tax_use": tax.type_tax_use,
        }

        res=self.onchange_base_amount(cr,uid,ids,base,tax_id)
        vals.update(res.get("value",{}))
        return {"value":vals}

    def onchange_base_amount(self,cr,uid,ids,base,tax_id):
        if not tax_id:
            return {}
        tax=self.pool.get("account.tax").browse(cr,uid,tax_id)
        res=self.pool.get("account.tax")._compute(cr, uid, [tax], base, 1.0)
        if not res:
            return {}
        vals={
            "tax_amount": res[0]["amount"],
        }
        return {"value":vals}

    def onchange_partner(self,cr,uid,ids,partner_id,tax_id=False,company_id=False):
        if not partner_id:
            return {}
        partner=self.pool.get("res.partner").browse(cr,uid,partner_id)

        #wht_type = self._get_wht_type(cr,uid,context={'partner_id':partner_id})

        vals={
            "partner_name": partner.name,
            "tax_id_no": partner.pid,
            #"wht_type": wht_type or 'pnd53'
        }
        if tax_id and company_id:
            vals['account_id']= self.onchange_tax(cr,uid,[],tax_id,0.0,partner_id,company_id)['value']['account_id']

        return {"value":vals}

    def btn_gen_no(self,cr,uid,ids,context={}):
        print 'btn_gen_no',ids
        if not ids:
            return
        for line in self.browse(cr,uid,ids,context=context):
            company_id = line.company_id.id
            context.update({'company_id':company_id,'process_date':line.date})

            if line.tax_id.tax_group!="wht" or line.tax_id.type_tax_use!="purchase":
                raise osv.except_osv(_("Error"),_("Can not generate document number for this type of tax"))
            if not line.partner_id:
                raise osv.except_osv(_("Error"),_("Missing partner cannot generate number"))
            if not line.wht_type:
                raise osv.except_osv(_("Error"),_("Missing WHT Type cannot generate number"))
            if not line.tax_id_no:
                raise osv.except_osv(_("Error"),_("Missing Tax ID No cannot generate number"))

            if not line.ref:
                #doc_no=self.pool.get('ir.sequence').get(cr,uid,'wht.line',context=context)
                #get latest sequence

                #TODO:fill all wht line with the same move_id
                #line.write({"ref":doc_no})
                extra_sql=''
                if line.payment_id:
                    extra_sql+=' and payment_id=%s ' % line.payment_id.id

                if line.invoice_id:
                    extra_sql+=' and invoice_id=%s ' % line.invoice_id.id

                if line.move_id:
                    extra_sql+=' and move_id=%s ' % line.move_id.id

                if line.company_id:
                    extra_sql+=' and company_id=%s ' % line.company_id.id

                if line.cheque_move_id:
                    extra_sql+=' and cheque_move_id=%s ' % line.cheque_move_id.id

                if line.bank_move_id:
                    extra_sql+=' and bank_move_id=%s ' % line.bank_move_id.id

                if line.petty_id:
                    extra_sql+=' and petty_id=%s ' % line.petty_id.id

                if line.advance_clear_id:
                    extra_sql+=' and advance_clear_id=%s ' % line.advance_clear_id.id

                #search all wht purchase
                cr.execute("""select id from account_tax where type_tax_use='purchase' and tax_group='wht' """)
                taxes = map(lambda x:x[0],cr.fetchall())

                #Search existing reference
                cr.execute('''select ref from account_tax_line
                        where partner_id=%s and date=%s and tax_id in %s and ref is not null '''+extra_sql,(line.partner_id.id,line.date,tuple(taxes),))
                res = map(lambda x:x[0],cr.fetchall())

                if res:
                    #if it already exist update it
                    cr.execute('''update account_tax_line set ref=%s where id=%s ''',(res[0],line.id,))

                else:
                    doc_no= self.pool.get('ir.sequence').get_nohole(cr,uid,'wht.line',"account_tax_line","ref",context=context)
                    cr.execute('''update account_tax_line set ref=%s
                            where partner_id=%s and date=%s and tax_id in %s '''+extra_sql,(doc_no,line.partner_id.id,line.date,tuple(taxes),))
        return True

    def button_open(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'open'})
        return True

    def button_cancel(self,cr,uid,ids,context=None):
        if isinstance(ids,(int,long)):
            ids=[ids]

        for obj in self.browse(cr,uid,ids):
            if not obj.move_id and obj.type_tax_use=='purchase' and obj.tax_group=='wht':
                self.write(cr,uid,obj.id,{'ref':False})

        cr.execute(""" update account_tax_line set state='canceled' where id in %s """,(tuple(ids),))
        return True

    def unlink(self,cr,uid,ids,context=None):
        cr.execute("""
        select id from account_tax_line where move_id is not null and id in %s

        """,(tuple(ids),))
        res = cr.fetchall()

        if res:
            #cannot delete tax line
            raise osv.except_osv(_('Warning !'), _('ไม่สามารถลบข้อมูลได้ เนื่องจากได้เชื่อมโยงการบันทึกบัญชีแล้ว'))

        return super(account_tax_line,self).unlink(cr,uid,ids,context)

    def update_sql(self,cr,uid,context=None):
        cr.execute("""
                UPDATE account_tax_line
                SET tax_id_no=i.tin
                FROM
                  (SELECT p.tin ,
                          tl.id
                   FROM account_tax_line tl,
                        res_partner p
                   WHERE tl.partner_id=p.id
                     AND tl.tax_id_no!=p.tin
                     AND p.tin IS NOT NULL) i
                WHERE i.id=account_tax_line.id
        """)
        cr.execute("""
                UPDATE
                account_tax_line
                SET period_id=i.period_id ,
                    company_id=i.company_id
                FROM
                  ( SELECT tl.id,
                           m.period_id,
                           m.company_id
                   FROM account_tax_line tl,
                        account_move m
                   WHERE m.id=tl.move_id
                     and tl.period_id is null) i
                WHERE account_tax_line.id=i.id
        """)
        cr.execute("""
                UPDATE account_tax_line
                SET wht_type=i.wht_type
                FROM
                  (SELECT p.wht_type ,
                          tl.id
                   FROM account_tax_line tl,
                        res_partner p
                   WHERE tl.partner_id=p.id
                     AND tl.wht_type IS NULL
                     AND p.wht_type IS NOT NULL
                     AND p.wht_type!=tl.wht_type) i
                WHERE i.id=account_tax_line.id
        """)
        return True
account_tax_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
