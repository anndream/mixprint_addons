# -*- encoding: utf-8 -*-
import os
import pyPdf
#from osv import osv
#import xmlrpclib
#import cStringIO as StringIO

#jy_serv = xmlrpclib.ServerProxy("http://localhost:9999/")

def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('utf-8')

def decode_vals(vals): #need to format for str and unicode object-
    dc={}
    for k,v in vals.items():
        k,v = unicode(k),safe_unicode(v) # key and value must the same type str,str
        dc[k]=v
    return dc

def pdf_fill(orig_pdf, vals):
    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    vals=decode_vals(vals)
    orig_pdf_abs=os.path.join(os.getcwd(),orig_pdf)
    tmp=os.tempnam()
    #tmp='/Users/tititab/Documents/demo.pdf'
    #print 'filling pdf',orig_pdf,tmp,vals
    #jy_serv.pdf_fill(orig_pdf_abs,tmp,vals)
    arg = ''
    for key in vals.keys():
        arg = arg + "%s='%s' " % (key, vals[key])
    #arg = arg.encode('cp874')
    arg = arg.encode('utf-8')
    cmd = "jython %s/openerp/addons/ineco_thai_account/report/fillpdf.py %s %s %s" % (os.getcwd(), orig_pdf_abs, tmp, arg)
    #print cmd
    os.system(cmd)
    pdf=file(tmp).read()
    os.unlink(tmp)
    return pdf

def pdf_merge(pdf1, pdf2):
    try:
        tmp1=os.tempnam()
        tmp2=os.tempnam()
        tmp3=os.tempnam()
        output = pyPdf.PdfFileWriter()
        file(tmp1,"w").write(pdf1)
        file(tmp2,"w").write(pdf2)
        input1 = pyPdf.PdfFileReader(file(tmp1, "rb"))
        input2 = pyPdf.PdfFileReader(file(tmp2, "rb"))
        for page in range(input1.getNumPages()):
            output.addPage(input1.getPage(page))
        for page in range(input2.getNumPages()):
            output.addPage(input2.getPage(page))
        outputStream = file(tmp3, "wb")
        output.write(outputStream)
        outputStream.close()
        #cmd="/usr/bin/pdftk %s %s cat output %s"%(tmp1,tmp2,tmp3)
        #os.system(cmd)
        pdf3=file(tmp3).read()
        os.unlink(tmp1)
        os.unlink(tmp2)
        os.unlink(tmp3)
        return pdf3
    except:
        raise Exception("Failed to merge PDF files")
