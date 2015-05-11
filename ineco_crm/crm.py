# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

# 2013-02-10     POP-001    ADD New notification on sale user
from datetime import datetime, timedelta
from openerp.osv import fields, osv
import time
#import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

#POP-001
class crm_phonecall(osv.osv):
    _inherit = 'crm.phonecall'
    _columns = {
        'create_user_id': fields.many2one('res.users', 'Created By'),
        'new_customer': fields.boolean('New Customer'),
        'visit': fields.boolean('Visit'),
    }
    _defaults = {
        'create_user_id': lambda self,cr,uid,ctx: uid,
        'new_customer': False,
        'visit': False,
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}         
        for phone in self.browse(cr, uid, ids, context=context):
            if phone.partner_id:
                self.pool.get("res.partner").write(cr, uid, [phone.partner_id.id], {'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S')})                                   
        return super(crm_phonecall, self).write(cr, uid, ids, vals, context=context)
    
    #Copy from Original
    def convert_opportunity(self, cr, uid, ids, opportunity_summary=False, partner_id=False, planned_revenue=0.0, probability=0.0, context=None):
        partner = self.pool.get('res.partner')
        opportunity = self.pool.get('crm.lead')
        opportunity_dict = {}
        default_contact = False
        for call in self.browse(cr, uid, ids, context=context):
            if not partner_id:
                partner_id = call.partner_id and call.partner_id.id or False
            if partner_id:
                partner.write(cr, uid, [partner_id], {'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S')})
                address_id = partner.address_get(cr, uid, [partner_id])['default']
                if address_id:
                    default_contact = partner.browse(cr, uid, address_id, context=context)
            opportunity_id = opportunity.create(cr, uid, {
                            'name': opportunity_summary or call.name,
                            'planned_revenue': planned_revenue,
                            'probability': probability,
                            'parquotation_mixprint_20130205_1_2_1tner_id': partner_id or False,
                            'mobile': default_contact and default_contact.mobile,
                            'section_id': call.section_id and call.section_id.id or False,
                            'description': call.description or False,
                            'priority': call.priority,
                            'type': 'opportunity',
                            'phone': call.partner_phone or False,
                            'email_from': default_contact and default_contact.email,
                        })
            vals = {
                    'partner_id': partner_id,
                    'opportunity_id' : opportunity_id,
            }
            self.write(cr, uid, [call.id], vals)
            self.case_close(cr, uid, [call.id])
            opportunity.case_open(cr, uid, [opportunity_id])
            opportunity_dict[call.id] = opportunity_id
        return opportunity_dict

    #Copy from Original
    def case_close(self, cr, uid, ids, context=None):
        """ Overrides close for crm_case for setting duration """
        res = True
        for phone in self.browse(cr, uid, ids, context=context):
            phone_id = phone.id
            data = {}
            if phone.duration <=0:
                duration = datetime.now() - datetime.strptime(phone.date, DEFAULT_SERVER_DATETIME_FORMAT)
                data['duration'] = duration.seconds/float(60)
            res = super(crm_phonecall, self).case_close(cr, uid, [phone_id], context=context)
            self.write(cr, uid, [phone_id], data, context=context)
            if phone.partner_id:
                self.pool.get("res.partner").write(cr, uid, [phone.partner_id.id], {'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res
    
    #Copy from Original
    def _call_create_partner(self, cr, uid, phonecall, context=None):
        partner = self.pool.get('res.partner')
        partner_id = partner.create(cr, uid, {
                    'name': phonecall.name,
                    'user_id': phonecall.user_id.id,
                    'comment': phonecall.description,
                    'address': [],
                    'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return partner_id

    def create(self, cr, uid, vals, context=None):
        obj_id = super(crm_phonecall, self).create(cr, uid, vals, context)
        if 'user_id' in vals:
            users = self.pool.get('res.users').browse(cr, uid, vals['user_id'] )
            self.message_subscribe(cr, uid, [obj_id], [users.partner_id.id], context=context)
            newid = self.message_post(cr, uid, [obj_id], body="Please read new phone call.", context=context)
            notification = self.pool.get('mail.notification')
            data = {
                'partner_id': users.partner_id.id,
                'message_id': newid,
                'read': False,
            }
            notification.create(cr, uid, data)
        return obj_id
    
    
class ineco_crm_reason(osv.osv):
    """ Category of Reason """
    _name = "ineco.crm.reason"
    _description = "Category of Reason"
    _columns = {
        'name': fields.char('Name', size=254, required=True),
    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Reason Name must be unique!')
    ]

class crm_lead(osv.osv):
    
    def _last_date_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for lead in self.browse(cr, uid, ids, context=context):
            last_date_count = 0
            sql = """
               select extract(days from now() - create_date) as age from crm_lead where id = %s
            """
            if lead.state not in ('done','cancel'):
                #date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                #date_start = datetime.strptime(lead.create_date,'%Y-%m-%d %H:%M:%S')
                #date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                #last_date_count = (date_finished-date_start).days 
                cr.execute(sql % (lead.id))
                last_date_count = cr.fetchone()[0] or 0.0
            res[lead.id] = last_date_count 
        return res

    def _my_opportunity(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for lead in self.browse(cr, uid, ids, context=context): 
            sql = """select crm_lead.create_uid as lead_uid, res_partner.create_uid as partner_uid from crm_lead
                     left join res_partner on crm_lead.partner_id = res_partner.id where crm_lead.id = %s"""
            cr.execute(sql % (lead.id))
            result = cr.dictfetchone()
            create_uid = result['lead_uid']
            partner_uid = result['partner_uid']
            if create_uid == lead.user_id.id == partner_uid:       
                res[lead.id] = True
            else:
                res[lead.id] = False
        return res
    
    _name = "crm.lead"
    _description = "Add Reason of LEAD/OPPORTUNITY"
    _inherit = "crm.lead"
    _columns = {
        'last_date_count': fields.function(_last_date_count, type="integer", string='Age',
            store={
                'crm.lead': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            }, help="The amount without tax.", track_visibility='always'),
        'reason_ids': fields.many2many('ineco.crm.reason', 'crm_lead_reason_rel', 'lead_id', 'reason_id', 'Reasons'),
        'date_lead_to_opportunity': fields.datetime('Date Lead to Opportunity'),
        'date_opportunity_to_quotation': fields.datetime('Date Lead to Opportunity'),
        'date_lose': fields.datetime('Date Lose'),
        'is_owned': fields.function(_my_opportunity, type="boolean", string='My Opportunity',
            store={
                'crm.lead': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            }),
        'last_contact_date': fields.related('partner_id', 'last_date_count', type='integer', string="Update", readonly=True), #store=True
    }
    
    _defaults = {
        'referred': lambda s, cr, uid, c: s.pool.get('res.users').browse(cr, uid, uid).name,
    }

    def create(self, cr, uid, data, context=None):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        data['referred'] = user.name
        return super(crm_lead, self).create(cr, uid, data, context=context)

    def case_reset(self, cr, uid, ids, context=None):
        """ Overrides case_reset from base_stage to set probability """
        res = super(crm_lead, self).case_reset(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'probability': 0.0, 
                                  'date_closed': False, 
                                  'date_lose': False, 
                                  'date_lead_to_opportunity': False, 
                                  'date_opportunity_to_quotation':False}, context=context)
        return res

    def case_mark_lost(self, cr, uid, ids, context=None):
        """ Mark the case as lost: state=cancel and probability=0 """
        for lead in self.browse(cr, uid, ids):
            stage_ids = self.pool.get('crm.case.stage').search(cr, uid, [('type','=','opportunity'),('state','=','cancel')])
            if stage_ids:
                self.case_set(cr, uid, [lead.id], values_to_update={'probability': 0.0, 
                                                                    'date_closed': time.strftime("%Y-%m-%d %H:%M:%S"),
                                                                    'date_lose': time.strftime("%Y-%m-%d %H:%M:%S")}, new_stage_id=stage_ids[0], context=context)
        return True

    def case_mark_won(self, cr, uid, ids, context=None):
        """ Mark the case as won: state=done and probability=100 """
        for lead in self.browse(cr, uid, ids):
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 100.0),('on_change','=',True)], context=context)
            if stage_id:
                self.case_set(cr, uid, [lead.id], values_to_update={'probability': 100.0, 
                                                                    'date_closed': time.strftime("%Y-%m-%d %H:%M:%S")}, new_stage_id=stage_id, context=context)
        return True
    
    def convert_opportunity(self, cr, uid, ids, partner_id, user_ids=False, section_id=False, context=None):
        customer = False
        if partner_id:
            partner = self.pool.get('res.partner')
            customer = partner.browse(cr, uid, partner_id, context=context)
        for lead in self.browse(cr, uid, ids, context=context):
            if lead.state in ('done', 'cancel'):
                continue
            vals = self._convert_opportunity_data(cr, uid, lead, customer, section_id, context=context)
            #Lead to Opportunity default datetime
            vals['date_lead_to_opportunity'] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.write(cr, uid, [lead.id], vals, context=context)
        self.message_post(cr, uid, ids, body=_("Lead <b>converted into an Opportunity</b>"), subtype="crm.mt_lead_convert_to_opportunity", context=context)

        if user_ids or section_id:
            self.allocate_salesman(cr, uid, ids, user_ids, section_id, context=context)

        return True

class crm_make_sale(osv.osv_memory):
    """ Make sale  order for crm """

    _inherit = "crm.make.sale"

    def makeOrder(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        if context is None:
            context = {}
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No addresse(s) defined for this customer.'))

                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'shop_id': make.shop_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.date.context_today(self,cr,uid,context=context),
                    'fiscal_position': fpos,
                    'lead_id': case.id,
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id, 
                                                    'date_opportunity_to_quotation': time.strftime("%Y-%m-%d %H:%M:%S"),
                                                    })
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
            if make.close:
                case_obj.case_close(cr, uid, data)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
