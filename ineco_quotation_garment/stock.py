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

# from lxml import etree
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
import time
# from operator import itemgetter
# from itertools import groupby

from openerp.osv import fields, osv
from openerp import tools
#from tools.translate import _
from openerp import netsvc
#import tools
#from tools import float_compare
import openerp.addons.decimal_precision as dp
# import logging
# _logger = logging.getLogger(__name__)

class ineco_delivery_objective(osv.osv):
    _name = 'ineco.delivery.objective'
    _description = "Objective to delivery something"
    _columns = {
        'name': fields.char('Description', size=128),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]

class ineco_delivery_type(osv.osv):
    _name = "ineco.delivery.type"
    _description = "Delivery Type"
    _columns = {
        'name': fields.char('Description', size=128),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _description = 'Add Sale Quantity'
    _columns = {
        'product_sale_qty': fields.float('Sale Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
        'color_id': fields.many2one('sale.color', 'Color'),
        'gender_id': fields.many2one('sale.gender', 'Gender'),
        'size_id': fields.many2one('sale.size', 'Size'),        
        'note': fields.char('Note', size=32,),
        'product_weight': fields.float('Weight', digits_compute=dp.get_precision('Product Unit of Measure')),
    }

    def unlink(self, cr, uid, ids, context=None):
        for id in ids:
            sql = "delete from ineco_picking_cost where move_id = %s"
            cr.execute(sql % id)
        return super(stock_move, self).unlink(cr, uid, ids, context=context)
    
    def create(self, cr, user, vals, context=None):
        new_id = super(stock_move, self).create(cr, user, vals, context)
        product_id = vals.get('product_id',False)
        if product_id:
            product_obj = self.pool.get('product.product').browse(cr, user, [product_id])[0]
            move_obj = self.browse(cr, user, [new_id])[0]
            if product_obj.categ_id.cost_type_ids and move_obj.picking_id and move_obj.picking_id.stock_journal_id and move_obj.picking_id.stock_journal_id.auto_costing :
                line_obj = self.pool.get('ineco.picking.cost')
                for cost in product_obj.categ_id.cost_type_ids:
                    found_ids = line_obj.search(cr, user, [('move_id','=',new_id),('cost_type_id','=',cost.cost_type_id.id)])
                    if not found_ids:
                        new_data = {
                            'name': '...',
                            'move_id': new_id,
                            'cost_type_id': cost.cost_type_id.id,
                            'cost': cost.cost,
                            'quantity': cost.quantity or vals.get('product_qty', 0.0 ) or 1.0,
                            'picking_id': vals.get('picking_id',False),
                        }
                        line_obj.create(cr, user, new_data)
        return new_id
    
class stock_picking_in(osv.osv):

    def _get_quantity(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = 0.0
            #res[stock.id] = {'quantity': 0.0}
            sql = "select sum(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id] = product_qty
        return res    

    def _get_record(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = 0.0
            #res[stock.id] = {'quantity': 0.0}
            sql = "select count(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id] = product_qty
        return res    

    def _get_overlimit(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = False
            #res[stock.id] = {'quantity': 0.0}
            sql = """
                select 
                 coalesce(sum(sjp.quantity),0)::integer as total_limit,
                 coalesce(sum(sm.product_qty),0)::integer as total_demand
                from stock_picking sp
                join stock_move sm on sp.id = sm.picking_id
                join product_product pp on pp.id = sm.product_id
                join product_template pt on pp.product_tmpl_id = pt.id
                join stock_journal_product sjp on sjp.product_categ_id = pt.categ_id
                where 
                   sp.id = %s
            """
            cr.execute(sql % stock.id)
            output = cr.dictfetchall()
            for r in output:
                limit =  r['total_limit'] 
                demand = r['total_demand'] 
            res[stock.id] = demand > limit 
        return res    
    
    _inherit = 'stock.picking.in'
    _columns = {
        'quantity': fields.function(_get_quantity, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='Quantity',
                                    type="float",),
        'record_count': fields.function(_get_record, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='#',
                                    type="integer",),
        'is_overlimit': fields.function(_get_overlimit, string='Over Limit', type="boolean",)
    }
    
class stock_picking_out(osv.osv):
    
    def _get_quantity(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = 0.0
            #res[stock.id] = {'quantity': 0.0}
            sql = "select sum(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id] = product_qty
        return res    

    def _get_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()

    def _get_record(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = 0.0
            #res[stock.id] = {'quantity': 0.0}
            sql = "select count(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id] = product_qty
        return res    

    def _get_overlimit(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = False
            if stock.stock_journal_id:
                #res[stock.id] = {'quantity': 0.0}
                sql = """
                    select 
                     coalesce(sum(sjp.quantity),0)::integer as total_limit,
                     coalesce(sum(sm.product_qty),0)::integer as total_demand
                    from stock_picking sp
                    join stock_move sm on sp.id = sm.picking_id
                    join product_product pp on pp.id = sm.product_id
                    join product_template pt on pp.product_tmpl_id = pt.id
                    join stock_journal_product sjp on sjp.product_categ_id = pt.categ_id and sjp.stock_journal_id = %s
                    where 
                       sp.id = %s
                """
                cr.execute(sql % (stock.stock_journal_id.id, stock.id))
                output = cr.dictfetchall()
                for r in output:
                    limit =  r['total_limit'] 
                    demand = r['total_demand'] 
                res[stock.id] = demand > limit 
        return res    
        
    _inherit = "stock.picking.out"
    _columns = {
        'delivery_type_id': fields.many2one('ineco.delivery.type','Delivery Type'),
        'shiping_cost': fields.float('Shipping Cost', digits_compute=dp.get_precision('Account')),
        'batch_no': fields.integer('Batch No'),
        'ineco_date_delivery': fields.date('Actual Delivery Date'),
        'garment_order_no': fields.related('sale_id', 'garment_order_no', type="char", string="Garment No", readonly=True),
        'date_delivery': fields.related('sale_id', 'date_delivery', type="date", string="Delivery Date", readonly=True),
        'picking_transfer_id': fields.many2one('stock.picking','Transfers Doc'),
        'quantity': fields.function(_get_quantity, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='Quantity',
                                    type="float",
            #store={
            #    'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 10),
            #    'stock.move': (_get_picking, ['product_qty'], 10),
            #},
            #multi='sums', help="Summary Product."
            ),
        'opportunity_id': fields.many2one('crm.lead', 'Opportunity',domain=[('type','=','opportunity')]),
        'objective_id': fields.many2one('ineco.delivery.objective', 'Objective'),
        'cost_ids': fields.one2many('ineco.picking.cost','picking_id'),
        'record_count': fields.function(_get_record, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='#',
                                    type="integer",),
        'is_overlimit': fields.function(_get_overlimit, string='Over Limit', type="boolean",)
    }
        
    def button_stop_production(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids):
            if picking.sale_id:
                sql = """
                    update mrp_production
                    set name = name || '#STOP'
                    where sale_order_id = %s 
                """ % picking.sale_id.id 
                sql = sql + """ and name not like '%STOP%'"""
                cr.execute(sql)
        return True

    def button_get_queue(self, cr, uid, ids, context=None):
        obj_seq = self.pool.get('ir.sequence')
        for picking in self.browse(cr, uid, ids):
            next_number = obj_seq.next_by_code(cr, uid, 'ineco.shipping', context=context)
            picking.write({'account_internal_no': next_number})
        return True
    
class stock_picking(osv.osv):

    def _get_quantity(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = {'quantity': 0.0}
            sql = "select sum(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id]['quantity'] = product_qty
        return res    
    
    def _get_productions(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            #res[stock.id] = {'production_list': False}
            production_list = ""
            for production in stock.production_ids:
                production_list = production_list + production.name + ", "
            #res[stock.id]['production_list'] = production_list
            res[stock.id] = production_list
        return res

    def _get_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()

    def _get_record(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = 0.0
            #res[stock.id] = {'quantity': 0.0}
            sql = "select count(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id] = product_qty
        return res    

    def _get_overlimit(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = False
            #res[stock.id] = {'quantity': 0.0}
            sql = """
                select 
                 coalesce(sum(sjp.quantity),0)::integer as total_limit,
                 coalesce(sum(sm.product_qty),0)::integer as total_demand
                from stock_picking sp
                join stock_move sm on sp.id = sm.picking_id
                join product_product pp on pp.id = sm.product_id
                join product_template pt on pp.product_tmpl_id = pt.id
                join stock_journal_product sjp on sjp.product_categ_id = pt.categ_id and sjp.stock_journal_id = %s
                where 
                   sp.id = %s
            """
            cr.execute(sql % (stock.stock_journal_id.id,stock.id))
            output = cr.dictfetchall()
            for r in output:
                limit =  r['total_limit'] 
                demand = r['total_demand'] 
            res[stock.id] = demand > limit 
        return res    
    
    _inherit = "stock.picking"
    _columns = {
        'order_color': fields.char('Color',size=64),
        'order_type': fields.char('Type', size=64),
        'order_weight': fields.char('Weight', size=64),
        'picking_note_id': fields.many2one('ineco.picking.note', 'Picking Note',),
        'quantity': fields.function(_get_quantity, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='Quantity',
                                    type="float",
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            },
            multi='sums', help="Summary Product."),
        'production_list': fields.function(_get_productions,
                                           string="Production List",
                                           type="char",
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['production_ids'], 10),
            }, ),
        'record_count': fields.function(_get_record, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='#',
                                    type="integer",),
        'is_overlimit': fields.function(_get_overlimit, string='Over Limit', type="boolean",)
    }

    def onchange_note_id(self, cr, uid, ids, note_id=False, context=None):
        note_obj = self.pool.get('ineco.picking.note')
        if not note_id:
            return {'value':{}}
        val = {}
        note = note_obj.read(cr, uid, note_id, ['note'],context=context)
        val['note'] = note.get('note', False) and note.get('note') or False
        return {'value': val}

#     def name_get(self, cr, uid, ids, context=None):
#         if not ids:
#             return []
#         reads = self.read(cr, uid, ids, ['name'], context)
#         res = []
#         for record in reads:
#             name = record['name']
#             res.append((record['id'], name))
#         return res
    
    def action_done(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        picking_obj = self.pool.get("stock.picking")
        journal_obj = self.pool.get('stock.journal')
        journal_ids = journal_obj.search(cr, uid, [('transfer_fg','=',True)])
        location_production_id = 7
        location_stock_id = 12
        data = self.browse(cr, uid, ids)[0]
        data_out = self.pool.get('stock.picking.out').browse(cr, uid, ids)[0]
        if data.is_overlimit:
            raise osv.except_osv('Over Product Limit Error!', 'Some product over limitation.')
        sql = """
            select 
             coalesce(sum(sjp.quantity),0)::integer as total_limit
            from stock_picking sp
            join stock_move sm on sp.id = sm.picking_id
            join product_product pp on pp.id = sm.product_id
            join product_template pt on pp.product_tmpl_id = pt.id
            join stock_journal_product sjp on sjp.product_categ_id = pt.categ_id and sjp.stock_journal_id = %s 
            where 
               sp.id = %s
        """ % (data.stock_journal_id.id, data.id)
        cr.execute(sql)
        check_qty = cr.fetchone()[0] or 0.0
        group_ids = self.pool.get('res.users').read(cr, uid, uid)['groups_id']
        group_warehous_manager_id = 28
        if group_warehous_manager_id not in group_ids and check_qty > 0:
            raise osv.except_osv('Permission denied!', 'Some product required Warehouse Manager Group to complete this document.')
        
        if data_out.picking_transfer_id:
            picking_obj.action_done_draft(cr, uid, [data_out.picking_transfer_id.id])
            wf_service.trg_validate(uid, 'stock.picking', data_out.picking_transfer_id.id, 'button_cancel', cr)
        production_obj = self.pool.get('mrp.production')
        production = production_obj.search(cr, uid, [('origin','ilike',data.origin)])
        new_picking = False
        if production:
            new_picking = picking_obj.copy(cr, uid, data.id,
                                {
                                    'name': '/',
                                    'type': 'internal',
                                    'stock_journal_id': journal_ids and journal_ids[0] or False,
                                    'state':'draft',

                                })
            new_data = self.browse(cr, uid, [new_picking])[0]
            for move in new_data.move_lines:
                move.write({'location_id': location_production_id, 
                            'location_dest_id': location_stock_id,
                            'state': 'done' })
            new_data.write({'state':'done'})

        self.pool.get('stock.picking.out').write(cr, uid, ids, {'ineco_date_delivery': time.strftime('%Y-%m-%d'),
                                                                'picking_transfer_id': new_picking or False})
        result = super(stock_picking, self).action_done(cr, uid, ids, context)
        return result 
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]
            query_args = {'name': search_name}
            limit_str = ''
            if limit:
                limit_str = ' limit %(limit)s'
                query_args['limit'] = limit
            cr.execute('''
                select stock_picking.id from stock_picking
                join res_partner on stock_picking.partner_id = res_partner.id
                where            
                  (stock_picking.name ''' + operator +''' %(name)s
                  or res_partner.name ''' + operator +''' %(name)s) '''+ limit_str, query_args)
            ids = map(lambda x: x[0], cr.fetchall())
            if args:
                ids = self.search(cr, uid, [('id', 'in', ids)] + args, limit=limit, context=context)
            if ids:
                return self.name_get(cr, uid, ids, context)
        return super(stock_picking,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)    

class stock_move_split_lines_exist(osv.osv_memory):
    _inherit = "stock.move.split.lines"
    _columns = {
        'product_weight': fields.float('Weight', digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    
class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
            if 'product_id' in fields:
                res.update({'product_id': move.product_id.id})
            if 'product_uom' in fields:
                res.update({'product_uom': move.product_uom.id})
            if 'qty' in fields:
                res.update({'qty': move.product_qty})
            if 'use_exist' in fields:
                res.update({'use_exist': (move.picking_id and move.picking_id.type=='out' and True) or False})
            if 'location_id' in fields:
                res.update({'location_id': move.location_id.id})
            if 'product_weight' in fields:
                res.update({'product_weight': move.product_weight})
        return res
    
    def split(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into serial numbers

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = {}
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'
        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool.get('stock.production.lot')
        inventory_obj = self.pool.get('stock.inventory')
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                if data.use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    prodlot_id = False
                    if data.use_exist:
                        prodlot_id = line.prodlot_id.id
                    if not prodlot_id:
                        prodlot_id = prodlot_obj.create(cr, uid, {
                            'name': line.name,
                            'product_id': move.product_id.id,
                            'ref': move.prodlot_id.ref or False},
                        context=context)

                    move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state, 'product_weight':line.product_weight or 0.0})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move
    
class ineco_picking_note(osv.osv):
    _name = 'ineco.picking.note'
    _columns = {
        'name': fields.char('description', size=128, reqruied=True),
        'note': fields.text('Note', required=True),
        'seq': fields.integer('Sequence')
    }
    _order = 'seq'
    _defaults = {
        'seq': 0,
    }
    
class stock_jouranl_product(osv.osv):
    _name = 'stock.journal.product'
    _columns = {
        'name': fields.char('...', size=32),
        'stock_journal_id': fields.many2one('stock.journal','Stock Journal'),
        'product_categ_id': fields.many2one('product.category','Product Category',required=True),
        'quantity': fields.integer('Quantity Limit', required=True),
    }
    _defaults = {
        'quantity': 1,
    }
    _order = 'stock_journal_id'
    
class stock_journal(osv.osv):
    _inherit = 'stock.journal'
    _columns = {
        'transfer_fg': fields.boolean('Is Transfer FG'),
        'auto_costing': fields.boolean('Auto Costing'),
        'product_ids': fields.one2many('stock.journal.product','stock_journal_id','Product Limit'),
    }
    
class ineco_cost_group(osv.osv):
    _name = 'ineco.cost.group'
    _description = "Cost Group"
    _columns = {
        'name': fields.char('Group Name', size=128, required=True),
    }

class ineco_cost_type(osv.osv):
    _name = "ineco.cost.type"
    _description = "cost Type"
    _columns = {
        'name': fields.char('Description', size=128),
        'cost': fields.integer('Cost'),
        'seq': fields.integer('Sequence'),
        'cost_group_id': fields.many2one('ineco.cost.group','Group'),
        'account_journal_id': fields.many2one('account.journal','Journal'),
        'product_id': fields.many2one('product.product','Default Product'),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]
    _order = 'seq'
    
class ineco_picking_cost(osv.osv):

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.quantity * line.cost
            res[line.id] = price
        return res

    def on_change_costtype(self, cr, uid, ids, cost_type_id, context=None):
        if context==None:
            context={}
        result = 0.0
        cost_type_obj = self.pool.get('ineco.cost.type').browse(cr, uid, cost_type_id)
        if cost_type_obj:
            result = cost_type_obj.cost
        return {'value': {
            'cost': result,
            }
        }
    
    _name = 'ineco.picking.cost'
    _description = "Cost of Delivery"
    _columns = {
        'name': fields.char('Description', size=128),
        'picking_id': fields.many2one('stock.picking.out', 'Delivery Order'),
        'cost_type_id': fields.many2one('ineco.cost.type','Cost Type'),
        'quantity': fields.integer('Quantity', required=True),
        'cost': fields.float('Cost', required=True),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'move_id': fields.many2one('stock.move','Move'),
        'date': fields.date('Date'),
        'doc_number': fields.char('Document No', size=32),
        'invoice_id': fields.many2one('account.invoice', 'Invoice')
    }
    
    _defaults = {
        'quantity': 1,
        'cost': 0.0,
        'date': time.strftime('%Y-%m-%d'),
    }
    
    def _prepare_invoice(self, cr, uid, cost, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        invoice_vals = {
            'name': cost.cost_type_id.name + ' : ' + cost.doc_number or False,
            'origin': cost.picking_id.origin or False,
            'type': inv_type,
            'account_id': account_id,
            'partner_id': partner.id,
            'comment': False,
            'payment_term': payment_term,
            'fiscal_position': partner.property_account_position.id,
            'date_invoice': cost.date,
            'company_id': cost.picking_id.company_id.id,
            'user_id': uid,
        }
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        return invoice_vals

    def _prepare_invoice_line(self, cr, uid, cost, invoice_id, product_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        name = cost.cost_type_id.name
        origin = cost.doc_number or False
        account_id = product_id.property_account_income.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = product_id.uom_id.id or False
        return {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'product_id': product_id.id,
            'account_id': account_id,
            'price_unit': cost.cost,
            'discount': 0.0,
            'quantity': cost.quantity,
            'invoice_line_tax_id': False,
            'account_analytic_id': False,
        }
    
    def button_create_invoice(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        wf_service = netsvc.LocalService('workflow')
        for data in self.browse(cr, uid, ids):
            if data.cost_type_id and data.cost_type_id.account_journal_id and data.cost_type_id.product_id:
                partner_id = False
                if data.picking_id.sale_id.partner_invoice_id.parent_id:
                    partner_id = data.picking_id.sale_id.partner_invoice_id.parent_id
                else:
                    partner_id = data.picking_id.sale_id.partner_invoice_id
                invoice_vals = self._prepare_invoice(cr, uid, data, 
                                                     partner_id,
                                                     'out_invoice' ,
                                                     data.cost_type_id.account_journal_id.id,
                                                     context)
                invoice_id = invoice_obj.create(cr, uid, invoice_vals)
                invoice_line_vals = self._prepare_invoice_line(cr, uid, data, invoice_id, data.cost_type_id.product_id, invoice_vals, context)
                invoice_line_obj.create(cr, uid, invoice_line_vals)
                data.write({'invoice_id': invoice_id})
                wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
            else:
                raise osv.except_osv('Error!', 'Not Account Journal or Product in Cost Type' % (data.cost_type_id.name))
        return True

class ineco_sale_lose_opportunity_costtemp(osv.osv):
    _name = 'ineco.sale.lose.opportunity.costtemp'
    _auto = False
    _columns = {
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity_costtemp')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity_costtemp AS
            select *
            from 
            (select cl.id as opportunity_id, 'opportunity' as type, ict.id as cost_type_id, icc.cost, icc.quantity, icc.quantity * icc.cost as amount from crm_lead cl
            join ineco_crm_cost icc on icc.lead_id = cl.id
            join ineco_cost_type ict on ict.id = icc.cost_type_id
            union 
            select cl.id as opportunity_id, 'shipping' as type, ict.id as cost_type_id, ipc.cost, ipc.quantity, ipc.quantity * ipc.cost as amount from stock_picking sp
            join crm_lead cl on sp.opportunity_id = cl.id
            join ineco_picking_cost ipc on sp.id = ipc.picking_id
            join ineco_cost_type ict on ict.id = ipc.cost_type_id) a
        """)

class ineco_opportunity_cost(osv.osv):
    _name = 'ineco.opportunity.cost'
    _auto = False
    _columns = {
        'opportunity_id': fields.many2one('crm.lead','Opportunity'),
        'type': fields.selection([('shipping','Shipping'),('opportunity','Opportunity')], 'Type'),
        'cost_type_id': fields.many2one('ineco.cost.type','Cost Type'),
        'cost': fields.integer('Cost'),
        'quantity': fields.integer('Quantity'),
        'amount': fields.integer('Amount'),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_opportunity_cost')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_opportunity_cost AS
            select id, (a1[id]).*
                from (
                    select a1, generate_series(1, array_upper(a1,1)) as id
                        from (
                            select array (
                                select ineco_sale_lose_opportunity_costtemp from ineco_sale_lose_opportunity_costtemp
                            ) as a1
                    ) b1
                ) c1
        """)    
        
class ineco_stock_packing(osv.osv):
    _name = 'ineco.stock.packing'
    _description = "Stock Packing"
    _columns = {
        'name': fields.char('Packing No', size=32, required=True),
        'sale_order_id': fields.many2one('sale.order','Sale Order'),
        'garment_order_no': fields.related('sale_order_id','garment_order_no', type="char", string="Garment No", readonly=True),
        'customer_id': fields.related('sale_order_id','partner_id',type="many2one", relation="res.partner", string="Customer", readonly=True),
        'sequence': fields.integer('Sequence'),
        'total': fields.integer('Total'),
        'date': fields.date('Date'),
        'line_ids': fields.one2many('ineco.stock.packing.line','packing_id','Packing Items'),
        'weight': fields.float('Weight',digits=(12,2)),
        'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],'State',readonly=True)
    }
    _defaults = {
        'name': '/',
        'sequence': 1.0,
        #'date': time.strftime('%Y-%m-%d'),
        'total': 1.0,
        'state': 'draft',
    }

    def button_cancel(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            for line in data.line_ids:
                if line.state == 'done':
                    raise osv.except_osv('Error!', 'Some line (%s) has done state.' % (line.product_id.name))
            data.write({'state':'cancel'})
        return True
    
    def button_done(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            for line in data.line_ids:
                line.button_done()
            data.write({'state':'done'})
        return True
    
    def button_load(self, cr, uid, ids, context=None):
        obj_picking = self.pool.get('stock.picking')
        obj_packing_line = self.pool.get('ineco.stock.packing.line')
        for data in self.browse(cr, uid, ids):
            picking_ids = obj_picking.search(cr, uid, [('sale_id','=', data.sale_order_id.id),('state','not in',['done','cancel'])])
            for picking in self.pool.get('stock.picking').browse(cr, uid, picking_ids):
                for move in picking.move_lines:
                    new_data = {
                        'stock_move_id': move.id,
                        'packing_id': data.id,
                    }
                    obj_packing_line.create(cr, uid, new_data)
        return True

    def button_reset(self, cr, uid, ids, context=None):
        obj_packing_line = self.pool.get('ineco.stock.packing.line')
        for data in self.browse(cr, uid, ids):
            line_ids = obj_packing_line.search(cr, uid, [('packing_id','=',data.id),('quantity','=',False)])
            if line_ids:
                obj_packing_line.unlink(cr, uid, line_ids)
        return True
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'ineco.packing.box') or '/'
        return super(ineco_stock_packing, self).create(cr, uid, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default = default.copy()
        default['line_ids'] = []
        default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'ineco.packing.box')
        return super(ineco_stock_packing, self).copy(cr, uid, id, default, context=context)
    
class ineco_stock_packing_line(osv.osv):
    _name = 'ineco.stock.packing.line'
    _description = "Stock Packing Line"
    _columns = {
        'name': fields.char('Description', size=32),
        'packing_id': fields.many2one('ineco.stock.packing','Packing'),
        'stock_move_id': fields.many2one('stock.move','Stock Move'),
        'product_id': fields.related('stock_move_id','product_id',type="many2one", relation="product.product", string="Product", readonly=True),
        'color_id': fields.related('stock_move_id', 'color_id', type="many2one", relation='sale.color', string='Color',readonly=True),
        'gender_id': fields.related('stock_move_id', 'gender_id', type="many2one", relation='sale.gender', string='Gender',readonly=True),
        'size_id': fields.related('stock_move_id', 'size_id', type="many2one", relation='sale.size', string='Size',readonly=True),
        'note': fields.related('stock_move_id','note', type="char", string="Note", readonly=True),
        'product_qty': fields.related('stock_move_id', 'product_qty', type="float",  string='Origin Qty',readonly=True),
        'quantity': fields.integer('Quantity'),
        'state': fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True)
    }
    _defaults = {
        'state': 'draft',
    }
    
    def button_done(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        prodlot_obj = self.pool.get('stock.production.lot')
        for data in self.browse(cr, uid, ids):
            if data.stock_move_id and data.stock_move_id.product_qty >= data.quantity:
                seq = data.packing_id.sequence or 1.0
                prodlot_ids = prodlot_obj.search(cr, uid, [('name','=',seq),('product_id','=',data.product_id.id)])
                prodlot_id = False
                if not prodlot_ids:
                    prodlot_id = prodlot_obj.create(cr, uid, {'name':seq,'product_id':data.product_id.id})
                else:
                    prodlot_id = prodlot_ids[0]
                default_val = {
                    'product_qty': data.quantity,
                    'product_uos_qty': data.quantity,
                    'state': 'assigned',
                    'prodlot_id': prodlot_id,
                }
                weight = 0.0
                if data.id == data.packing_id.line_ids[0].id:
                    weight = data.packing_id.weight
                    default_val.update({'product_weight': weight})
                    print weight
                if data.stock_move_id.product_qty == data.quantity:
                    if data.state != 'done':
                        move_obj.write(cr, uid, [data.stock_move_id.id],{'prodlot_id':prodlot_id,'state':'assigned','product_weight': weight})
                else:
                    if data.state != 'done':
                        new_move_id = move_obj.copy(cr, uid, data.stock_move_id.id, default_val, context=context)
                        move_obj.write(cr, uid, [data.stock_move_id.id],{'product_qty':data.stock_move_id.product_qty - data.quantity,
                                                                         'state':'assigned'})
                data.write({'state':'done'})
        return True
