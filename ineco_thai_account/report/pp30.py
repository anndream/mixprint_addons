# -*- encoding: utf-8 -*-
from report.interface import report_int
from report_tools import pdf_fill, pdf_merge
from openerp.osv import fields, osv

import pooler
from num2word import num2word_th
import datetime

def fmt_tin(tin):
    return "%s %s%s%s%s %s%s%s%s%s %s%s %s"%(tin[0],tin[1],tin[2],tin[3],tin[4],tin[5],tin[6],tin[7],tin[8],tin[9],tin[10],tin[11],tin[12])

def set_satang(vals):
    for key in vals.keys():
        if key.startswith("tax"):
            amt=vals[key]
            vals[key]=int(amt)
            vals[key.replace("tax","st")]=int(amt*100.0)%100

def fmt_thaidate(date):
    dt=datetime.datetime.strptime(date,"%Y-%m-%d")
    return "%2d/%d/%d"%(dt.day,dt.month,dt.year+543) 


class report_custom(report_int):
    def create(self,cr,uid,ids,datas,context={}):
        #print "WHT PND3 Report"      
        pool=pooler.get_pool(cr.dbname)
        lang=pool.get("res.lang").browse(cr,uid,1)      
        user=pool.get("res.users").browse(cr,uid,uid)
        pdf = False
        for id in ids:
            vouch = pool.get("account.period").browse(cr,uid,id)          
            company = vouch.company_id
            
            yearnow=int(vouch.date_pp30[0:4])+543
            monthnow=int(vouch.date_pp30[5:7])
            daynow=int(vouch.date_pp30[8:10])
                            
#             daynow = datetime.datetime.now().day
#             monthnow  = datetime.datetime.now().month
#             yearnow = int(datetime.datetime.now().year)+543
                        
                
            sale_untax = vouch.sale_amount_untaxed - vouch.sale_refund_amount_untaxed + (vouch.sale_receipt_amount_untaxed - vouch.sale_receipt_amount_tax)
            sale_tax = vouch.sale_amount_tax - vouch.sale_refund_amount_tax + vouch.sale_receipt_amount_tax
            purchase_untax = vouch.purchase_amount_untaxed - vouch.purchase_refund_amount_untaxed + (vouch.purchase_receipt_amount_untaxed - vouch.purchase_receipt_amount_tax)
            purchase_tax = vouch.purchase_amount_tax - vouch.purchase_refund_amount_tax + vouch.purchase_receipt_amount_tax
            
    
            vals={
                "Text1":company.ineco_tax and fmt_tin(company.ineco_tax) or "",
                "Text57":company.ineco_branch or '',
                "name_place":company.ineco_company_name,                
                "number":company.ineco_building or '',
                "room_no":company.ineco_room_no or '',
                "floor":company.ineco_class or '',
                "village":company.ineco_village or '',
                "add_no":company.ineco_no or '',
                "moo":company.ineco_moo or '',
                "soi":company.ineco_alley or '',
                "road":company.ineco_road or '',
                "district":company.ineco_district or '',
                "amphur":company.ineco_amphoe or '',
                "province":company.ineco_province or '',
                "Text58":company.ineco_zip or '',
                "tel":company.ineco_phone or '',
                "year":yearnow,
                "Text53":lang.format("%.2f",sale_untax,grouping=True).replace("."," "),
                "Text47":lang.format("%.2f",sale_untax,grouping=True).replace("."," "),
                "Text30":lang.format("%.2f",sale_tax,grouping=True).replace("."," "),
                "Text51":lang.format("%.2f",purchase_untax,grouping=True).replace("."," "),
                "Text52":lang.format("%.2f",purchase_tax,grouping=True).replace("."," "),       
                "signature4": company.ineco_name or '',
                "date":str(daynow)+"/"+ str(monthnow)+"/"+ str(yearnow),   
              
            }
            if sale_tax >= purchase_tax:
                vat = sale_tax - purchase_tax
                vals.update({
                             "Text34":lang.format("%.2f",vat,grouping=True).replace("."," "),
                             "Text38":lang.format("%.2f",vat,grouping=True).replace("."," "), 
                             "'Check Box11'": "Yes",
                             })
            else:
                vat = purchase_tax - sale_tax
                vals.update({
                             "Text35":lang.format("%.2f",vat,grouping=True).replace("."," "),
                             "Text39":lang.format("%.2f",vat,grouping=True).replace("."," "), 
                             "'Check Box12'": "Yes",
                             })                

            pdf2=pdf_fill("openerp/addons/ineco_thai_account/report/pdf/pp30.pdf",vals)
            if pdf:
                pdf = pdf_merge(pdf, pdf2)
            else:
                pdf = pdf2
                
        return (pdf, "pdf")

report_custom("report.pp30")
