
openerp.oepetstore = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.oepetstore = {};

    instance.oepetstore.HomePage = instance.web.Widget.extend({
        template: "HomePage",
        events: {
        	keydown: 'onKeydown',
        	onload: 'onload',
        },
        start: function() {
            var pettoys = new instance.oepetstore.PetToysList(this);
            pettoys.appendTo(this.$(".oe_petstore_homepage_left"));
            var motd = new instance.oepetstore.MessageOfTheDay(this);
            motd.appendTo(this.$(".oe_petstore_homepage_right"));
            //document.getElementById('fname').focus();
        },
        onKeydown: function (e) {
            var sel;          
            var self = this;
            switch (e.which) {
            case $.ui.keyCode.ENTER:      
            	console.log('Key Enter Down!');
            	/*self.do_action({
                    views: [[false, 'form']],
                    view_type: 'form',
                    view_mode: 'form',
                    res_model: 'product.product',
                    type: 'ir.actions.act_window',
                    target: 'new',
                    readonly: 1,
                    res_id: 3,
            	});*/        
            	document.getElementById('comments').value = document.getElementById('fname').value;
            	document.getElementById('fname').value='OK Naja';
            	//$("#form [name='fname']").focus();
            	//document.getElementById('fname').focus();
                //e.preventDefault();
                break;
            }
        },
        onload: function (e) {
            var self = this;
            console.log('Loading!');
            document.getElementById('fname').value='';
            document.getElementById('fname').focus();
        },
    });

    instance.web.client_actions.add('petstore.homepage', 'instance.oepetstore.HomePage');

    instance.oepetstore.MessageOfTheDay = instance.web.Widget.extend({
        template: "MessageofTheDay",
        init: function() {
            this._super.apply(this, arguments);
        },
        start: function() {
            var self = this;
            new instance.web.Model("message_of_the_day").query(["message"]).first().then(function(result) {
                self.$(".oe_mywidget_message_of_the_day").text(result.message);
            });
        },
    });

    instance.oepetstore.PetToysList = instance.web.Widget.extend({
        template: "PetToysList",
        start: function() {
            var self = this;
            new instance.web.Model("product.product").query(["name", "image"])
                .filter([["categ_id.name", "=", "Pet Toys"]]).all().then(function(result) {
                _.each(result, function(item) {
                    var $item = $(QWeb.render("PetToy", {item: item}));
                    self.$el.append($item);
                });
            });
        },
    });

}