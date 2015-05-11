# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 INECO LTD, PARTNERSHIP (<http://www.ineco.co.th>).
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

#
#4-03-2012        POP-001        Create

import time
from lxml import etree

from osv import fields, osv
from tools.translate import _

import pooler
import base

from base import ir


class wizard_ineco_report_remove(osv.osv_memory):

    def act_cancel(self, cr, uid, ids, context=None):
        #self.unlink(cr, uid, ids, context)
        return {'type':'ir.actions.act_window_close' }

    def act_destroy(self, *args):
        return {'type':'ir.actions.act_window_close' }

    def do_action(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', []), 'id':context.get('active_id',[])}
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        pool = pooler.get_pool(cr.dbname)
        report = pool.get('ir.actions.report.xml').browse(cr, uid, datas['ids'][0], context=context)

        report_ids = pool.get('ir.values').search(cr, uid, [('value','=',report.type+','+str(datas['ids'][0]))])
        for report_id in report_ids:
            pool.get('ir.values').unlink(cr, uid, report_id)
        return self.write(cr, uid, ids, {'state':'get'}, context=context)

    _name = "wizard.ineco.report.remove"
    _description = "Remove Report Button"

    _columns = {
        'state': fields.selection( ( ('choose','choose'), ('get','get'), ) ),
    }
    _defaults = { 
        'state': lambda *a: 'choose',
    }    

wizard_ineco_report_remove()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
