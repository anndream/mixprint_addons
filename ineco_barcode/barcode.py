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

from openerp import tools
from openerp.osv import fields, osv, orm
import logging

_logger = logging.getLogger(__name__)
try:
    from reportlab.graphics.barcode import getCodes
except ImportError:
    _logger.warning('unable to import reportlab')
    
def _get_code(self, cr, uid, context=None):
    return [(r, r) for r in getCodes()]

class ineco_barcode_config(orm.Model):
    
    _name = 'ineco.barcode.config'
    _columns = {
        'res_model_id': fields.many2one('ir.model', 'Object',required=True),
        'field_id': fields.many2one('ir.model.fields', 'Field'),
        'width': fields.integer("Width"),
        'height': fields.integer("Height"),
        'barcode_type': fields.selection(_get_code, 'Type', required=True),
        'prefix': fields.char('Prefix', size=8, required=True),
    }
    
    _sql_constraints = [
        ('res_model_uniq',
         'unique(res_model)',
         'You can have only one config by model !'),
        ('prefix_uniq',
         'unique(prefix)',
         'You can have only one config by prefix !')
    ]
    
class ineco_barcode_temp(osv.osv):
        
    _name = 'ineco.barcode.temp'
    _description = 'Ineco Barcode Temp'
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_barcode_temp')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_barcode_temp AS (
select * from (
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'stock.picking')) as name,
    (select id from ir_model where model = 'stock.picking') as model_id from stock_picking
union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'stock.production.lot')) as name,
    (select id from ir_model where model = 'stock.production.lot') as model_id from stock_production_lot
union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'mrp.production')) as name,
    (select id from ir_model where model = 'mrp.production') as model_id from mrp_production
union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'product.product')) as name,
    (select id from ir_model where model = 'product.product') as model_id from product_product
union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'hr.employee')) as name,
    (select id from ir_model where model = 'hr.employee') as model_id from hr_employee
union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'ineco.pattern')) as name,
    (select id from ir_model where model = 'ineco.pattern') as model_id from ineco_pattern
union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'ineco.mrp.pattern.component')) as name,
    (select id from ir_model where model = 'ineco.mrp.pattern.component') as model_id from ineco_mrp_pattern_component
union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'mrp.workcenter')) as name,
    (select id from ir_model where model = 'mrp.workcenter') as model_id from mrp_workcenter
    union
select id as res_id,
    concat(id,':',(select id from ir_model where model = 'mrp.production.workcenter.line')) as name,
    (select id from ir_model where model = 'mrp.production.workcenter.line') as model_id from mrp_production_workcenter_line
) a
            )""")
        
class ineco_barcode(osv.osv):
    _name = "ineco.barcode"
    _auto = False
    _description = "INECO Barcode"
    _columns = {
        'res_id':fields.integer('Resource Id', readonly=True),
        'name': fields.char('Code',size=64, readonly=True),
        'model_id': fields.many2one('ir.model', 'Model', readonly=True),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_barcode')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_barcode AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_barcode_temp from ineco_barcode_temp
                            ) as a
                    ) b
                ) c
            )""")
  