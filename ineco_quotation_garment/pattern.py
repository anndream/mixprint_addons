# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITE (<http://www.ineco.co.th>).
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

from openerp.osv import osv, fields
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.osv.orm import Model


#import openerp.addons.decimal_precision as dp

class ineco_pattern(osv.osv):

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def _get_late(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        today = datetime.now()
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'late': False
            }
            if obj.date_start and not obj.sampling_date_start_planned and not obj.garment_order_no:
                start_date = datetime.strptime(obj.date_start, '%Y-%m-%d %H:%M:%S') + relativedelta(days=3)
                if today > start_date:
                    result[obj.id]['late'] = True
                else:
                    result[obj.id]['late'] = False
            elif obj.sampling_date_start_planned and not obj.sampling_date_finish_planned :
                start_date = datetime.strptime(obj.date_start, '%Y-%m-%d %H:%M:%S') + relativedelta(days=3)
                if today > start_date:
                    result[obj.id]['late'] = True
                else:
                    result[obj.id]['late'] = False 
            elif obj.garment_order_no and obj.date_start and not obj.date_finish_planned :
                start_date = datetime.strptime(obj.date_start, '%Y-%m-%d %H:%M:%S') + relativedelta(days=3)
                if today > start_date:
                    result[obj.id]['late'] = True
                else:
                    result[obj.id]['late'] = False
            else:
                result[obj.id]['late'] = False            
        return result

    def _get_collar(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'collar_day': False
            }
            if obj.date_collar_finish:
                result[obj.id] = {
                    'collar_day': '%02d' % int(obj.date_collar_finish.split('-')[1])
                }
        return result

    def _get_date_collar_planned(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'date_collar_planned': False
            }
            production_ids = self.pool.get('mrp.production').search(cr, uid, [('sale_order_id','=',obj.saleorder_id.id)])
            min_date = False
            for production in self.pool.get('mrp.production').browse(cr, uid, production_ids):
                min_date = max(min_date, production.date_process1_start or False)
            if min_date:
                result[obj.id] = {
                    'date_collar_planned': min_date
                }
        return result
    
    def _get_attachment(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'attachment_count': False
            }
            sql = """
                    select count(*) from ir_attachment 
                    where res_model = 'ineco.pattern' and res_id = %s
                """ % obj.id
            cr.execute(sql)             
            data = cr.fetchone()
            if data and data[0]:
                result[obj.id]['attachment_count'] = data[0] or 0.0
        return result

    def _get_attachment_search(self, cr, uid, obj, name, args, context=None):
        """ Searches Ids of products
        @return: Ids of locations
        """
        pattern = self.pool.get('ineco.pattern').search(cr, uid, [])
        sql = """select res_id, 1 from ir_attachment 
                 where res_model = 'ineco.pattern' and res_id IN %s 
                 group by res_id 
                 union
                 select id, 1 from ineco_pattern
                 where pattern_id is not null 
                 """ % str(tuple(pattern),)
        cr.execute(sql)
        res = cr.fetchall()
        ids = [('id', 'not in', map(lambda x: x[0], res))]
        return ids

    def _get_product(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'product_name': False,
                'sale_product_id': False,
            }
            if obj.saleorder_id:
                sql = """
                    select 
                      pt.name,
                      pp.id
                    from sale_order so
                    join sale_order_line sol on so.id = sol.order_id
                    join product_product pp on sol.product_id = pp.id
                    join product_template pt on pp.product_tmpl_id = pt.id 
                    where so.id = %s and pt.type not in ('service')
                    limit 1
                """ % obj.saleorder_id.id
                cr.execute(sql)             
                data = cr.fetchone()
                if data and data[0]:
                    result[obj.id]['product_name'] = data[0] or ''
                    result[obj.id]['sale_product_id'] = data[1] or False
        return result

    def _get_original_mo(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'garment_order_no_org': False
            }
            if obj.saleorder_id:
                sql = """
                    select
                      garment_order_no
                    from sale_order
                    where name = (
                    select
                      origin
                    from 
                      sale_order so
                    where
                      so.id = %s)
                  """ % obj.saleorder_id.id
                cr.execute(sql)             
                data = cr.fetchone()
                if data and data[0]:
                    result[obj.id]['garment_order_no_org'] = data[0] or ''
        return result

    def _get_quantity(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'order_qty': False
            }
            if obj.saleorder_id:
                sql = """
                    select 
                      coalesce(sum(sol.product_uom_qty), 0) as quantity
                    from
                      sale_order_line sol
                      join product_product pp on sol.product_id = pp.id
                      join product_template pt on pt.id = pp.product_tmpl_id
                    where order_id = %s
                      and pt.type <> 'service'                    
                  """ % obj.saleorder_id.id
                cr.execute(sql)             
                data = cr.fetchone()
                if data and data[0]:
                    result[obj.id]['order_qty'] = data[0] or 0.0
        return result

    def _get_production_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for pattern in self.browse(cr, uid, ids, context=context):
            res[pattern.id] = []
            if not pattern.saleorder_id:
                continue
            sale_order_id = pattern.saleorder_id.id
            result_ids = self.pool.get('mrp.production').search(cr, uid, [('sale_order_id','=',sale_order_id)])
            if result_ids:
                res[pattern.id] = sorted(result_ids)
        return res

    def _get_ticket_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for pattern in self.browse(cr, uid, ids, context=context):
            res[pattern.id] = []
            if not pattern.saleorder_id:
                continue
            sale_order_id = pattern.saleorder_id.id
            production_ids = self.pool.get('mrp.production').search(cr, uid, [('sale_order_id','=',sale_order_id)])
            if production_ids:
                result_ids = self.pool.get('ineco.mrp.production.ticket').search(cr, uid, [('production_id','in',production_ids)])
                if result_ids:
                    res[pattern.id] = sorted(result_ids)
        return res

    def _get_production_pattern(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('mrp.production').browse(cr, uid, ids, context=context):
            pattern_ids = self.pool.get('ineco.pattern').search(cr, uid, [('saleorder_id','=',line.sale_order_id.id)])
            for pattern in pattern_ids:
                result[pattern] = True
        return result.keys()
        
    _name = 'ineco.pattern'
    _inherit = ['mail.thread']
    _description = "Pattern"
    _columns = {
        'name': fields.char('Code', size=64, required=True, track_visibility='onchange'),
        'product_id': fields.many2one('product.product','Product',required=True),
        'saleorder_id': fields.many2one('sale.order','Sale Order', track_visibility='onchange'),
        'garment_order_no': fields.related('saleorder_id', 'garment_order_no', type='char', string='Garment Order No', readonly=True),
        'sampling_order_no': fields.related('saleorder_id', 'sample_order_no', type='char', string='Sampling Order No', readonly=True),
        'partner_id': fields.related('saleorder_id', 'partner_id', type='many2one', relation='res.partner', string='Customer', readonly=True),
        'product_type_id': fields.many2one('ineco.pattern.product.type','Product Type',),
        'line_ids': fields.one2many('ineco.pattern.line','pattern_id','Lines'),
        'log_ids': fields.one2many('ineco.pattern.log','pattern_id','Logs'),
        'component_ids': fields.one2many('ineco.pattern.component','pattern_id','Components'),
        'gender_ids': fields.many2many('sale.gender', 'ineco_pattern_sale_gender_rel', 'child_id', 'parent_id', 'Gender'),
        'size_ids': fields.many2many('sale.size', 'ineco_pattern_sale_size_rel', 'child_id', 'parent_id', 'Size'),
        'state': fields.selection([('draft','Draft'),('ready','Ready'),('used','Used'),('damage','Damage')],'Status', readonly=True,
                                   track_visibility='onchange'),
        'last_updated': fields.datetime('Last Update'),
        'rev_no': fields.integer('Revision No'),
        'location_id': fields.many2one('ineco.pattern.location','Location',),
        'active': fields.boolean('Active'),
        'image': fields.binary('Image'),
        'multi_images': fields.text("Multi Images"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'ineco.pattern': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
            help="Medium-sized logo of the brand. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized photo", type="binary", multi="_get_image",
            store = {
                'ineco.pattern': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },
            help="Small-sized photo of the brand. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        #new requirement (sampling date suit)
        'date_expected': fields.datetime('Date Expected'),
        'employee_id': fields.many2one('hr.employee', 'Employee', track_visibility='onchange'),
        'sampling_date_start': fields.datetime('Date Start'),
        'sampling_date_start_planned': fields.datetime('Planned Start'),
        'sampling_date_finish_planned': fields.datetime('Planned Finish'),
        'sampling_date_finish': fields.datetime('Date Finish'),
        'sampling_date_mark_start': fields.datetime('Date Start'),
        'sampling_date_mark_finish': fields.datetime('Date Finish'),
        'sampling_marker': fields.char('Marker', size=32),
        'sampling_date_process1_start': fields.datetime('Date Start'),
        'sampling_date_process1_finish': fields.datetime('Date Finish'),
        'sampling_process1_employee': fields.char('Employee', size=32),
        'sampling_date_process2_start': fields.datetime('Date Start'),
        'sampling_date_process2_finish': fields.datetime('Date Finish'),
        'sampling_process2_employee': fields.char('Employee', size=32),
        #new mo date suit
        'date_start': fields.datetime('Date Start'),
        'date_start_planned': fields.datetime('Planned Start'),
        'date_finish_planned': fields.datetime('Planned Finish'),
        'date_finish': fields.datetime('Date Finish'),
        'date_mark_start': fields.datetime('Date Mark Start'),
        'date_mark_finish': fields.datetime('Date Mark Finish'),
        'marker': fields.char('Marker', size=32),
        'late': fields.function(_get_late, string="Late", type="boolean", multi="_late",
            store = {
                'ineco.pattern': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },),
        'user_id': fields.related('saleorder_id', 'user_id', type='many2one', relation="res.users", string='Sale', readonly=True),
        'product_name': fields.function(_get_product, string="Product", type="char", multi="_product"),
        'sale_product_id': fields.function(_get_product, string="Product", type="many2one", relation="product.product", multi="_product",
            store = {
                'ineco.pattern': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            }),
        'garment_order_no_org': fields.function(_get_original_mo, string="Master MO", type="char", multi="_mo"),
        'is_cancel': fields.boolean('Is Cancel'),
        'pattern_id': fields.many2one('ineco.pattern','Source Pattern'),
        'order_qty': fields.function(_get_quantity, string="Quantity", type="integer", multi="_quantity"),
        'schedule_update': fields.datetime('Schedule Update'),
        'note': fields.text('Note'),
        'remark2': fields.char('Remark 2', size=32),
        'attachment_count': fields.function(_get_attachment, fnct_search=_get_attachment_search, string="Attachment", type='integer', multi="_attachment"),
        'production_ids': fields.function(_get_production_lines, type='many2many', relation='mrp.production', string='Productions'),                
        'ticket_ids': fields.one2many('ineco.mrp.production.ticket','pattern_id','Tickets'),                
        'pattern_group_id': fields.many2one('ineco.pattern.group', 'Pattern Group'),
        'process_ids': fields.one2many('ineco.pattern.process','pattern_id','Processes'),

        #Collar
        'machine_collar_id': fields.many2one('ineco.mrp.machine', 'Collar Machine'),
        'employee_collar_id': fields.many2one('hr.employee', 'Collar Employee'),
        'date_collar_start': fields.date('Date Collar Start'),
        'date_collar_finish': fields.date('Date Collar Finish'),
        'collar_day': fields.function(_get_collar, string="Collar Day", type="char", size=2, multi="_collar",
            store = {
                'ineco.pattern': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            },),
        'date_collar_planned': fields.function(_get_date_collar_planned, string="Collar Planned", type="datetime", multi="_collar2",
            store = {
                'ineco.pattern': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'mrp.production': (_get_production_pattern, ['date_process1_start'], 10),
            },),
    }
    
    _sql_constraints = [
        ('name_unique', 'unique(name, pattern_group_id)', 'Code and Group must be unique!'),
    ]
    
    _defaults = {
        'active': True,
        'state': 'draft',
        'rev_no': 0,
        'size_ids': lambda self, cr, uid, c: [(6, 0, self.pool.get('sale.size').search(cr, uid, [], context=c, order='seq'))],    
        'is_cancel': False,  
        'remark2': False,
        'note': False,
        'date_collar_finish': False,
        'machine_collar_id': False,
        'employee_collar_id': False,
    }
    
    _order = 'date_start'

    def button_component(self, cr, uid, ids, context=None):
        for id in ids:
            pattern = self.browse(cr, uid, id)
            for production in pattern.production_ids:
                production.write({'pattern_id':pattern.id})
                production.button_component()
        return True

    def button_setdraft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft', 'date_finish_planned': False})
        return True

    def schedule_refresh(self, cr, uid, context={}):
        #print 'Refresh Partner Start'
        pattern_obj = self.pool.get('ineco.pattern')
        pattern_ids = pattern_obj.search(cr, uid, [('state','=','draft'),('date_finish_planned','=',False),('is_cancel','=',False)])
        if pattern_ids:
            pattern_obj.write(cr, uid, pattern_ids, {'schedule_update': time.strftime("%Y-%m-%d %H:%M:%S")})

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}

        default['last_updated'] = False
        default['line_ids'] = False
        default['log_ids'] = False
        data = self.browse(cr, uid, id, context=context)
        if not default.get('name', False):
            default.update(name="%s (copy)" % (data.name))
        res = super(ineco_pattern, self).copy(cr, uid, id, default, context)

        return res
    
    def button_master_pattern(self, cr, uid, ids, context=None):
        pattern_obj = self.pool.get('ineco.pattern')
        pattern_id = False
        for id in ids:
            data = self.browse(cr, uid, id)
            if data.garment_order_no_org:
                pattern_ids = pattern_obj.search(cr, uid, [('garment_order_no','=',data.garment_order_no_org)])
                #print data.garment_order_no_org, pattern_ids
                if pattern_ids:
                    if pattern_ids[0] != id:
                        pattern_id = pattern_ids[0]
                        data.write({'pattern_id': pattern_id})
        return True
        
    def button_pattern_copy(self, cr, uid, ids, context=None):
        for id in ids:
            data = self.browse(cr, uid, id, context=context)
            if data:
                pattern_id = data.pattern_id.id
                pattern_component_src_ids = self.pool.get('ineco.pattern.component').search(cr, uid, [('pattern_id','=',pattern_id)])
                component_obj = self.pool.get('ineco.pattern.component')
                for component in self.pool.get('ineco.pattern.component').browse(cr, uid, pattern_component_src_ids):
                    component_obj.create(cr, uid, {
                        'name': component.name,
                        'seq': component.seq,
                        'type_id': component.type_id.id,
                        'pattern_id': id,
                    })
        return True
    
    def button_ready(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'ready', 'date_finish': time.strftime('%Y-%m-%d'),'date_finish_planned':time.strftime('%Y-%m-%d')})
        return True

    def button_used(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'used'})
        return True

    def button_damage(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'damage'})
        return True
    
    def button_generate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for data in self.browse(cr, uid, ids):
            cr.execute('delete from ineco_pattern_line where pattern_id = %s' % (data.id))
            for gender in data.gender_ids:
                for size in data.size_ids:
                    for component in data.component_ids:
                        new_code = data.name[0:5] + component.type_id.code + \
                            gender.code + size.code + \
                            data.product_type_id.code
                        new_record = {
                            'name': new_code,
                            'gender_id': gender.id,
                            'size_id': size.id,
                            'type_id': component.type_id.id,
                            'pattern_id': data.id,
                        }
                        self.pool.get('ineco.pattern.line').create(cr, uid, new_record)
        return True
    
class ineco_pattern_type(osv.osv):
    _name = 'ineco.pattern.type'
    _description = 'Type of Pattern Line'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'code': fields.char('Code', size=10, required=True),
        'name2': fields.char('Other Description',size=64,required=True),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]   

class ineco_pattern_group(osv.osv):
    _name = 'ineco.pattern.group'
    _description = 'Group of Pattern'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]   

class ineco_pattern_location(osv.osv):
    _name = 'ineco.pattern.location'
    _description = 'Pattern Location'
    _columns = {
        'name': fields.char('Description',size=128,required=True),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]     
    
class ineco_pattern_product_type(osv.osv):
    _name = 'ineco.pattern.product.type'
    _description = 'Product Type of Pattern Line'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'code': fields.char('Code', size=10, required=True),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]   
    
class ineco_pattern_component(osv.osv):
    _name = 'ineco.pattern.component'
    _description = "Pattern Component"
    _columns = {
        'name': fields.char('Description',size=64,),
        'seq': fields.integer('Sequence'),
        'type_id': fields.many2one('ineco.pattern.type','Type',required=True),
        'last_updated': fields.datetime('Last Updated'),
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
    }
    _defaults = {
        'name': '...',
        #'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order = 'seq'
    
    def write(self, cr, uid, ids, vals, context=None):
        vals.update({'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")})
        res = super(ineco_pattern_component, self).write(cr, uid, ids, vals, context=context)
        return res    
        
class ineco_pattern_line(osv.osv):
    _name = 'ineco.pattern.line'
    _description = "Pattern Line"
    _columns = {
        'name': fields.char('Line Code',size=64,required=True),
        'gender_id': fields.many2one('sale.gender','Gender',required=True),
        'size_id': fields.many2one('sale.size','Size',required=True),
        'type_id': fields.many2one('ineco.pattern.type','Type',required=True),
        'last_updated': fields.datetime('Last Updated'),
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
    }
    _sql_constraints = [
        ('name_gender_size_type_pattern_unique', 'unique (name,gender_id,size_id,type_id,pattern_id)', 'Data must be unique !')
    ]   
    _defaults = {
        #'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    def write(self, cr, uid, ids, vals, context=None):
        vals.update({'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")})
        res = super(ineco_pattern_line, self).write(cr, uid, ids, vals, context=context)
        return res
    
class ineco_pattern_log(osv.osv):
    _name = "ineco.pattern.log"
    _description = "Pattern LOG"
    _columns = {
        'name': fields.char('Description',size=64,),
        'type': fields.selection([('in','In'),('out','Out')],'Type',required=True),
        'user_id': fields.many2one('hr.employee','User', required=True),
        'pattern_line_id': fields.many2one('ineco.pattern.line','Pattern Line',),
        'last_updated': fields.datetime('Last Updated'),    
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
    }
    _defaults = {
        #'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _order = 'last_updated desc'

    def create(self, cr, uid, vals, context=None):
        pattern_id = vals.get('pattern_id', False)
        type = vals.get('type', False)
        if pattern_id and type:
            pattern = self.pool.get('ineco.pattern').browse(cr, uid, [pattern_id])[0]
            if type == 'out' and pattern.state != 'damange':
                pattern.write({'state':'used'})
            elif type == 'in':
                pattern.write({'state':'ready'})
        vals.update({'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")})
        return super(ineco_pattern_log, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals.update({'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")})
        res = super(ineco_pattern_log, self).write(cr, uid, ids, vals, context=context)
        return res
    
class ineco_pattern_process(osv.osv):
    
    _name = 'ineco.pattern.process'
    _description = 'Process of Pattern'
    _columns = {
        'name': fields.char('Description',size=254,required=True),
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
        'process_id': fields.many2one('ineco.mrp.process','Process',required=True),
        'sequence': fields.integer('Seq',required=True),
        'cycle_time': fields.integer('Cycle Time (Sec.)',required=True),
        'cost': fields.integer('Cost',),
        'needle_length': fields.integer('Needle Length'),
        'level': fields.selection([('begin','Beginner'),('medium','Medium'),('hard','Hard')],'Level'),
        'image_multi': fields.text('Image List'),
        'attachments': fields.one2many('ir.attachment', 'pattern_process_id', string="Attachments"),
        'product_ids': fields.one2many('ineco.pattern.process.product','pattern_process_id','Accessories'),
    }
    _defaults = {
        'level': 'begin',
        'needle_length': 0.0,
    }

    def _get_sequence(self, cr, uid, context=None):
        context = context or {}
        next_id = False
        if context.get('lines', False):
            next_id = len(context.get('lines', False)) + 1
        else:
            next_id = 1
        return next_id
    
    _defaults = {
        'sequence': _get_sequence,
    }

    #_sql_constraints = [
    #    ('name_unique', 'unique (name)', 'Description must be unique !')
    #]   
    
class ineco_pattern_process_product(osv.osv):
    _name = 'ineco.pattern.process.product'
    _description = "Pattern Process Product"
    _columns = {
        'name': fields.char('Description',size=64),
        'pattern_process_id': fields.many2one('ineco.pattern.process','Pattern Process'),
        'product_id': fields.many2one('product.product','Product',required=True),
        'quantity': fields.float('Quantity'),
    }
    _defaults = {
        'quantity': 1.0,
        'name': '...',
    }

class document_file(Model):
    
    _inherit = 'ir.attachment'
    
    _columns = {
        'pattern_process_id': fields.many2one('ineco.pattern.process','Pattern Process'),
        'mrp_process_id': fields.many2one('ineco.mrp.process','MRP Process'),
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('pattern_process_id', 0) != 0 and not (vals.get('res_id', False) and vals.get('res_model', False)):
            vals['res_id'] = vals['pattern_process_id']
            vals['res_model'] = 'ineco.pattern.process'
        elif vals.get('mrp_process_id', 0) != 0 and not (vals.get('res_id', False) and vals.get('res_model', False)):
            vals['res_id'] = vals['mrp_process_id']
            vals['res_model'] = 'ineco.mrp.process'
        return super(document_file, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('pattern_process_id', 0) != 0 and not (vals.get('res_id', False) and vals.get('res_model', False)):
            vals['res_id'] = vals['pattern_process_id']
            vals['res_model'] = 'ineco.pattern.process'
        elif vals.get('mrp_process_id', 0) != 0 and not (vals.get('res_id', False) and vals.get('res_model', False)):
            vals['res_id'] = vals['mrp_process_id']
            vals['res_model'] = 'ineco.mrp.process'
        return super(document_file, self).write(cr, uid, ids, vals, context)
