# -*- coding: utf-8 -*-
##############################################################################
#
#    Poiesis Consulting, OpenERP Partner
#    Copyright (C) 2011 Poiesis Consulting (<http://www.poiesisconsulting.com>). All Rights Reserved.
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools
        
        
class base_config_settings(osv.osv_memory):
    _inherit = 'base.config.settings'
    
    _columns={
        'search_limit': fields.integer('Many2one search limit'),
    }
    
    def get_default_search_limit(self, cr, uid, ids, context=None):
        ir_conf_pool=self.pool.get('ir.config_parameter')
        search_limit=ir_conf_pool.get_param(cr, uid, 'search_limit', 7, context=context)
        search_limit=int(search_limit)
        return {'search_limit': search_limit}

    def set_search_limit(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        ir_conf_pool=self.pool.get('ir.config_parameter')
        ir_conf_pool.set_param(cr, uid, 'search_limit', config.search_limit, context=context)        
        
        
        