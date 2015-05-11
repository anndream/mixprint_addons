# -*- encoding: utf-8 -*-
from report.interface import report_int
from report_tools import pdf_fill, pdf_merge
#from pdf_tools import pdf_fill,pdf_merge
import pooler
from num2word import num2word_th

def fmt_tin(tin):
    return "%s %s%s%s%s %s%s%s%s%s %s%s %s"%(tin[0],tin[1],tin[2],tin[3],tin[4],tin[5],tin[6],tin[7],tin[8],tin[9],tin[10],tin[11],tin[12])

def fmt_addr(addr):
    s=""
    if addr.street:
        s+=addr.street
    if addr.street2:
        s+=" "+addr.street2
    if addr.city:
        s+=" "+addr.city
    if addr.state_id:
        s+=" "+addr.state_id.name
    if addr.zip:
        s+=" "+addr.zip
    return s

class report_custom(report_int):
    
    def create(self, cr, uid, ids, datas, context={}):
        #print "WHT certificate report"
        pool=pooler.get_pool(cr.dbname)
        lang=pool.get("res.lang").browse(cr,uid,1)
        user=pool.get("res.users").browse(cr,uid,uid)
        pdf = False
        for id in ids:
            vouch = pool.get("ineco.wht").browse(cr,uid,id)
            partner = vouch.company_id.partner_id
            supp = vouch.partner_id
    
            year=int(vouch.date_doc[0:4])+543
            month=int(vouch.date_doc[5:7])
            day=int(vouch.date_doc[8:10])
    
            totals={}
            #totals[line.tax_code_id.code]=vouch.base_amount
            #print "totals",totals
    
            vals={
                "name1": partner.name,
                "add1": fmt_addr(partner) or "",
                "tin1": partner.pid or "",
                "id1": partner.vat and fmt_tin(partner.vat) or "",
                "name2": supp.name,
                "add2": supp and fmt_addr(supp) or "",
                #"tin1_2": supp.pid or "",
                #"id1_2": supp.vat and fmt_tin(supp.vat) or "",
                "id1_2": fmt_tin(supp.pid) or "",
                "tin1_2": supp.vat and fmt_tin(supp.vat) or "",
                #"chk4": supp.vat and "Yes" or "",
                #"chk7": supp.pid and "Yes" or "",
                "chk4": vouch.wht_kind == 'pp3' and "Yes" or "",
                "chk7": vouch.wht_kind == 'pp7' and "Yes" or "",
                "date_pay": day,
                "month_pay": month,
                "year_pay": year,
            }
            #book_no
            vals.update({'book_no':'1'})
            #run no
            vals.update({'run_no':vouch.id})
            #ภงด
    #         vals.update({
    #             'chk1': "Yes",
    #             'chk2': "Yes",
    #             'chk3': "Yes",
    #             'chk5': "Yes",
    #             'chk6': "Yes",
    #             'chk7': "Yes",
    #         })
            if vouch.wht_kind == 'pp1':
                vals.update({'chk1': "Yes"})
            if vouch.wht_kind == 'pp2':
                vals.update({'chk2': "Yes"})
            if vouch.wht_kind == 'pp3':
                vals.update({'chk3': "Yes"})
            if vouch.wht_kind == 'pp4':
                vals.update({'chk4': "Yes"})
            if vouch.wht_kind == 'pp5':
                vals.update({'chk5': "Yes"})
            if vouch.wht_kind == 'pp6':
                vals.update({'chk6': "Yes"})
            if vouch.wht_kind == 'pp7':
                vals.update({'chk7': "Yes"})
            #ด้านล่าง
    #         vals.update({
    #             'chk8': "Yes",
    #             'chk9': "Yes",
    #             'chk10': "Yes",
    #             'chk11': "Yes",
    #         })
            if vouch.wht_payment == 'pm1':
                vals.update({'chk8': "Yes"})
            if vouch.wht_payment == 'pm2':
                vals.update({'chk9': "Yes"})
            if vouch.wht_payment == 'pm3':
                vals.update({'chk10': "Yes"})
            if vouch.wht_payment == 'pm4':
                vals.update({'chk11': "Yes"})
            
            #Item No
            vals.update({'item':vouch.seq or ""})
            
            #Spec unknow
            #vals.update({'spec1':'1'}) #Other 1
            #vals.update({'spec3':'2'}) #Other 2
            #vals.update({'spec4':'3'}) #Other 3
            
            total_base=vouch.base_amount
            total_tax=vouch.tax
    
            for line in vouch.line_ids:
                year = int(line.date_doc[0:4])+543
                month = int(line.date_doc[5:7])
                day = int(line.date_doc[8:10])
                if line.wht_type_id.seq == 100:
                    vals.update({
                        "date1": "%d-%d-%d"%(day,month,year),
                        "pay1.0": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.0": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 200:
                    vals.update({
                        "date2": "%d-%d-%d"%(day,month,year),
                        "pay1.1": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.1": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 300:
                    vals.update({
                        "date3": "%d-%d-%d"%(day,month,year),
                        "pay1.2": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.2": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 400:
                    vals.update({
                        "date4": "%d-%d-%d"%(day,month,year),
                        "pay1.3": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.3": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 411:
                    vals.update({
                        "date5": "%d-%d-%d"%(day,month,year),
                        "pay1.4": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.4": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 412:
                    vals.update({
                        "date6": "%d-%d-%d"%(day,month,year),
                        "pay1.5": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.5": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 413:
                    vals.update({
                        "date7": "%d-%d-%d"%(day,month,year),
                        "pay1.6": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.6": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 414:
                    vals.update({
                        #rate1
                        "rate1": "",
                        "date8": "%d-%d-%d"%(day,month,year),
                        "pay1.7": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.7": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 421:
                    vals.update({
                        "date9": "%d-%d-%d"%(day,month,year),
                        "pay1.8": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.8": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 422:
                    vals.update({
                        "date10": "%d-%d-%d"%(day,month,year),
                        "pay1.9": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.9": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 423:
                    vals.update({
                        "date11": "%d-%d-%d"%(day,month,year),
                        "pay1.10": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.10": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 425:
                    vals.update({
                        "spec1": line.name,
                        "date12": "%d-%d-%d"%(day,month,year),
                        "pay1.11": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.11": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 500:
                    vals.update({
                        "date13": "%d-%d-%d"%(day,month,year),
                        "pay1.12": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.12": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 600:
                    vals.update({
                        "spec3": line.note or vouch.note or line.wht_type_id.printed or 'ค่าบริการ',
                        "date14": "%d-%d-%d"%(day,month,year),
                        "pay1.13": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.13": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
    
            vals.update({
                "pay1.14": lang.format("%.2f",total_base,grouping=True).replace("."," "),
                "tax1.14": lang.format("%.2f",total_tax,grouping=True).replace("."," "),
                "total": num2word_th(total_tax,"th").decode('utf-8'),
            })
    
            pdf2=pdf_fill("openerp/addons/ineco_thai_account/report/pdf/wht_certif.pdf",vals)
            if pdf:
                pdf = pdf_merge(pdf, pdf2)
            else:
                pdf = pdf2
        return (pdf, "pdf")
    
report_custom("report.wht.certif")
