openerp.poi_limit_search = function(instance){

    var module = instance.point_of_sale;
    var _t = instance.web._t,
    _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    
    instance.web.form.FieldMany2One = instance.web.form.FieldMany2One.extend({
    	init: function(field_manager, node) {
            this._super(field_manager, node);
    		var self=this;
    		var P = new instance.web.Model('ir.config_parameter');
            P.call('get_param', ['search_limit']).then(function(search_limit) {
            	if (search_limit) {
            		self.limit=parseInt(search_limit);
            	}
            	else
            	{
            		self.limit = 7;
            	}
            	
            });
    	},
    });
    
}