
openerp.ineco_crm_dashboard = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.ineco_crm_dashboard = {};

    instance.ineco_crm_dashboard.HomePage = instance.web.Widget.extend({
        start: function() {
        	var self = this;
        	var srctext = "Not Found";
            new instance.web.Model("ineco.dashboard.story")
            		.query(["name","username","password","server","port"])
            		.first().then(function(result) {
		            	srctext = "src='http://"+result.server+":"+result.port+"/jasperserver/flow.html?_flowId=viewReportFlow"+
		                	"&amp;decorate=no"+
		                	"&amp;reportUnit="+result.name+
		                	"&amp;j_username="+result.username+
		                	"&amp;j_password="+result.password+
		                	"&amp;userLocale=en'"
		                self.iframe_text = "<iframe "+srctext+" frameBorder='0' width='100%' height='670px' />";
		            	self.$el.append(QWeb.render("HomePageTemplate",{name2:self.iframe_text}));
            		});        	
        },
    });
    
    instance.web.client_actions.add('ineco_dashboard.homepage', 'instance.ineco_crm_dashboard.HomePage');
}