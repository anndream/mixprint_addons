# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD,. PART. (<http://www.ineco.co.th>).
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



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import tools

import time
from openerp.osv import fields, osv
#import openerp.decimal_precision as dp
from openerp.tools.translate import _

class ineco_cash_flow(osv.osv):
    _name = 'ineco.cash.flow'
    _description = 'Cash Flow Class'
    _auto = False
    _columns = {
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_cash_flow_draft')
        cr.execute("""
            create or replace view ineco_cash_flow_draft as
            select 
              aml.date,
              rp.name as partner_name,
              case
                when aml.ref = aml.name then 
                  case 
                    when ic.name is not null then ic.name || '(' || aml.ref || ')'
                    else
                      aml.ref
                    end
                else 
                  case 
                    when aml.name not in ('-','/','.') then aml.ref || '(' || aml.name || ')'
                    else aml.ref
                  end 
              end as description,
              round(aml.debit,2) as debit,
              round(aml.credit,2) as credit
            from 
              account_move_line aml
              left join account_account aa on aa.id = aml.account_id
              left join res_partner rp on aml.partner_id = rp.id
              left join account_move am on aml.move_id = am.id
              left join account_voucher av on av.move_id = am.id
              left join ineco_cheque ic on ic.id = av.cheque_id
            where 
              aa.cashflow_report = true
              and aml.state = 'valid'
            order by
              aml.date   
        """)
        tools.drop_view_if_exists(cr, 'ineco_cash_flow_prepare')
        cr.execute("""
            create or replace view ineco_cash_flow_prepare as
                select 
                    id, 
                    (a[id]).* from (
                        select a, generate_series(1, array_upper(a,1)) as id from (
                            select array (
                                select ineco_cash_flow_draft from ineco_cash_flow_draft
                            ) as a 
                        ) as b 
                    ) as c;        
        """)
        tools.drop_view_if_exists(cr, 'ineco_cash_flow')
        cr.execute("""
            create or replace view ineco_cash_flow as
            select *, 
              (select sum(round(debit,2)) - sum(round(credit,2)) from ineco_cash_flow_prepare in1 where in1.id <= out1.id ) as balance 
            from ineco_cash_flow_prepare out1        
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
    