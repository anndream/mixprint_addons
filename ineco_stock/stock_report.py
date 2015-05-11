# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

#from lxml import etree
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
import time
#from operator import itemgetter
#from itertools import groupby

from openerp.osv import fields, osv
#from openerp.tools.translate import _
#from openerp import netsvc
from openerp import tools
#from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class query_stock_list_template(osv.osv):
    _name = "query.stock.list.template"
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'query_stock_list_template')
        cr.execute("""
        create or replace view query_stock_list_template as

select 
  pt.uom_id,
  move.*,
  coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end ) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id <> move.location_dest_id
                and location_dest_id = move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('done')
  ),0) -
  coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id = move.location_dest_id
                and location_dest_id <> move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('done')
  ),0) as on_hand,
  coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end ) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id <> move.location_dest_id
                and location_dest_id = move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('confirmed','waiting','assigned','done')
  ),0) -
  coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id = move.location_dest_id
                and location_dest_id <> move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('confirmed','waiting','assigned','done')
  ),0) as forecast  
from product_template pt
left join product_product pp on pp.product_tmpl_id = pt.id
left join product_uom pu on pt.uom_id = pu.id
left join 
  (select distinct 
    sm.product_id, 
    product_packaging, 
    prodlot_id, 
    sm.location_dest_id, 
    case when sl2.is_stock is null then 'OTHER' else 'STOCK' end as is_stock
   from stock_move sm
   left join stock_location sl1 on sm.location_id = sl1.id
   left join stock_location sl2 on sm.location_dest_id = sl2.id
   left join stock_production_lot spl on spl.id = sm.prodlot_id
   ) 
  as move on move.product_id = pp.id
order by default_code, prodlot_id, location_dest_id
        
        """)
    
class ineco_stock_list(osv.osv):
    _name = 'ineco.stock.list'
    _auto = False
    _columns = {
        'product_id': fields.many2one('product.product','Product',readonly=True),
        'product_packaging': fields.many2one('product.packaging','Packing', readonly=True),
        'prodlot_id': fields.many2one('stock.production.lot','Serial Number', readonly=True),
        'location_dest_id': fields.many2one('stock.location','Location',readonly=True),
        'is_stock': fields.char('Is Stock', size=32, readonly=True),
        'on_hand': fields.float('On Hand', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
        'forecast': fields.float('Forecast', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
        'uom_id': fields.many2one('product.uom', 'UOM' ,readonly=True),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_stock_list')
        cr.execute("""
create or replace view ineco_stock_list as

select 
  move.*,
  pt.uom_id,
  (coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end ) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id <> move.location_dest_id
                and location_dest_id = move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('done')
  ),0) -
  coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id = move.location_dest_id
                and location_dest_id <> move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('done')
  ),0)) * pu.factor as on_hand,
  (coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end ) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id <> move.location_dest_id
                and location_dest_id = move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('confirmed','waiting','assigned','done')
  ),0) -
  coalesce((
  select sum(product_qty * case when uom_type = 'reference' then round(factor,0) when uom_type = 'bigger' then round(1/factor,0) else round(factor,0) end) from stock_move
  left join product_uom on stock_move.product_uom = product_uom.id
                where location_id = move.location_dest_id
                and location_dest_id <> move.location_dest_id
                and product_id = move.product_id
                and
            case 
              when move.prodlot_id is not null then prodlot_id = move.prodlot_id 
              else prodlot_id is null
            end 
                and state in ('confirmed','waiting','assigned','done')
  ),0)) * pu.factor  as forecast
from product_template pt
left join product_product pp on pp.product_tmpl_id = pt.id
left join product_uom pu on pt.uom_id = pu.id
left join 
  (select distinct 
    min(sm.id) as id,
    sm.product_id, 
    product_packaging, 
    prodlot_id, 
    sm.location_dest_id, 
    case when sl2.is_stock is null then 'OTHER' else 'STOCK' end as is_stock
   from stock_move sm
   left join stock_location sl1 on sm.location_id = sl1.id
   left join stock_location sl2 on sm.location_dest_id = sl2.id
   left join stock_production_lot spl on spl.id = sm.prodlot_id
  group by
  sm.product_id, 
    product_packaging, 
    prodlot_id, 
    sm.location_dest_id, 
    case when sl2.is_stock is null then 'OTHER' else 'STOCK' end
      ) 
  as move on move.product_id = pp.id
order by default_code, prodlot_id, location_dest_id

            """)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: