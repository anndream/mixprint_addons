openerp.ineco_barcode = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.ineco_barcode = {};

    instance.web.client_actions.add('oebarcode.homepage', 'instance.ineco_barcode.HomePage');

    instance.ineco_barcode.HomePage = instance.web.Widget.extend({
        template: "HomePage",
        start: function() {
            var search = new instance.ineco_barcode.BarcodeSearch(this);
            search.appendTo(this.$(".oe_barcode_homepage_left"));
        },
    });

    instance.ineco_barcode.BarcodeSearch = instance.web.Widget.extend({
        template: "BarcodeSearch",
        events: {
        	keydown: 'onKeydown',
        },
        init: function() {
            this._super.apply(this, arguments);
        },
        start: function() {
            var self = this;
            $(".oe_barcode_search").focus();
        },
        onKeydown: function (e) {
            var sel;          
            var self = this;
            function supplier_render(product_id){        
            	var stock_move = new instance.web.Model("stock.move");
            	var stock_picking = new instance.web.Model("stock.picking");
            	stock_move.query()
            		.filter([["product_id.id", "=", product_id],["picking_id.type","=",'in']])
            	    .order_by('-date_stock_card')
            	    .first().then(function(move) {
            	    	if (move){
            	    		var picking_id = move.picking_id[0];
            	    		stock_picking.query().filter([["id","=",picking_id]]).first().then(function(picking) {
            	    			$(".oe_product_supplier").text(picking.partner_id[1]) ;
            	    		});
            	    	}
            	    	else {
            	    		$(".oe_product_supplier").text("Not Found!") ;
            	    	};
            	});
            };
            function last_purchase_render(product_id){          
            	new instance.web.Model("stock.move").query()
            		.filter([["product_id.id", "=", product_id],["picking_id.type","=",'in']])
            	    .order_by('-date_stock_card')
            	    .first().then(function(result3) {
            	    	if ((result3) && (result3.date)) {
            	    		$(".oe_product_lastpurchase").text(result3.date) ;
            	    	}
            	    	else {
            	    		$(".oe_product_lastpurchase").text("-");
            	    	} ;
            	});
            };
            function cost_render(product_id){        
            	var product_obj = new instance.web.Model("product.product");
            	product_obj.query()
            		.filter([["id", "=", product_id]])
            	    .first().then(function(product) {
            	    	if (product){
            	    		$(".oe_product_cost").text(product.standard_price) ;
            	    	}
            	    	else {
            	    		$(".oe_product_cost").text("-") ;
            	    	};
            	});
            };
            function render_customer_by_saleorder(saleorder_id){        
            	var sale_obj = new instance.web.Model("sale.order");
            	sale_obj.query()
            		.filter([["id", "=", saleorder_id]])
            	    .first().then(function(sale) {
            	    	if (sale){
            	    		$(".oe_mrp_customer_name").text(sale.partner_id[1]) ;
            	    	}
            	    	else {
            	    		$(".oe_mrp_customer_name").text("-") ;
            	    	};
            	});
            };
            function render_deliverydate_by_saleorder(saleorder_id){        
            	var sale_obj = new instance.web.Model("sale.order");
            	sale_obj.query()
            		.filter([["id", "=", saleorder_id]])
            	    .first().then(function(sale) {
            	    	if (sale){
            	    		$(".oe_mrp_date_delivery").text(sale.date_delivery) ;
            	    	}
            	    	else {
            	    		$(".oe_mrp_date_delivery").text("-") ;
            	    	};
            	});
            };
            function render_mrp_grandtotal(origin){        
            	if (origin){
            	
	            	var mrp_obj = new instance.web.Model("mrp.production");
	            	mrp_obj.query()
	            		.filter([["origin", "=", origin]])
	            	    .all().then(function(mrp) {
	            	    	if (mrp){
	            	    		var grandtotal = 0;
	            	    		_.each(mrp, function(item){
	            	    			grandtotal = grandtotal + item.product_qty;
	            	    		}) ;
	            	    		$(".oe_mrp_grand_total").text(grandtotal) ;
	            	    	}
	            	    	else {
	            	    		$(".oe_mrp_grand_total").text("-") ;
	            	    	};
	            	});
            	} ;
            };
            function render_product_by_saleorder(saleorder_id){        
            	if (saleorder_id){
            	
	            	var sale_obj = new instance.web.Model("sale.order.line");
	            	sale_obj.query()
	            		.filter([["order_id", "=", saleorder_id],['product_id.type','!=','service']])
	            	    .all().then(function(sale_line) {
	            	    	if (sale_line){
	            	    		var product_name = '';
	            	    		_.each(sale_line, function(item){
	            	    			product_name = item.product_id[1];
	            	    		}) ;
	            	    		$(".oe_sale_product").text(product_name) ;
	            	    	}
	            	    	else {
	            	    		$(".oe_sale_product").text("-") ;
	            	    	};
	            	});
            	} ;
            };
            function render_productqty_by_saleorder(saleorder_id){        
            	if (saleorder_id){
            	
	            	var sale_obj = new instance.web.Model("sale.order.line");
	            	sale_obj.query()
	            		.filter([["order_id", "=", saleorder_id],['product_id.type','!=','service']])
	            	    .all().then(function(sale_line) {
	            	    	if (sale_line){
	            	    		var total = 0;
	            	    		_.each(sale_line, function(item){
	            	    			total = total + item.product_uom_qty ;
	            	    		}) ;
	            	    		$(".oe_sale_quantity").text(total) ;
	            	    	}
	            	    	else {
	            	    		$(".oe_sale_quantity").text("-") ;
	            	    	};
	            	});
            	} ;
            };
            function location_render(product_id){        
            	var list_obj = new instance.web.Model("ineco.stock.list");
            	var location_obj = new instance.web.Model("stock.location");
            	var location_list = [];
            	list_obj.query()
            		.filter([["product_id.id", "=", product_id],['on_hand','!=',0.0],['is_stock','=','STOCK']])
            	    .all().then(function(list) {
            	    	$(".oe_product_locations").empty();
            	    	if (list){            	    	
            	    		var location_name = [];
            	    		_.each(list, function(item) {
            	    			//console.log(item.location_dest_id[0]) ;       
            	    			location_name = item.location_dest_id[1].split('/');
                	    		//location_list = location_list + location_name[location_name.length-1]+", ";            	    				
            	    			//console.log(location_name);
            	    			location_list.push(location_name[location_name.length-1]) ;
                            });
            	    		location_list = _.uniq(location_list) ;
            	    		//console.log(location_list) ;
            	    		$(".oe_product_locations").text(location_list) ;
            	    	};
            	});
            };
            function location_lot_render(lot_id){        
            	var list_obj = new instance.web.Model("ineco.stock.list");
            	var location_obj = new instance.web.Model("stock.location");
            	var location_list = [];
            	list_obj.query()
            		.filter([["prodlot_id.id", "=", lot_id],['on_hand','!=',0.0],['is_stock','=','STOCK']])
            	    .all().then(function(list) {
            	    	$(".oe_lot_location").empty();
            	    	if (list){            	    		
            	    		_.each(list, function(item) {
            	    			//console.log(item.location_dest_id[0]) ;       
            	    			var location_name = item.location_dest_id[1].split('/');
            	    			//console.log(location_name);
            	    			//location_list = location_list + location_name[location_name.length-1]+", \n";
            	    			location_list.push(location_name[location_name.length-1]) ;
                            });
            	    		//console.log(location_list);
            	    		location_list = _.uniq(location_list) ;
            	    		$(".oe_lot_location").text(location_list) ;
            	    	};
            	});
            };
            function picture_render(product_id){        
            	var product_obj = new instance.web.Model("product.product");
            	product_obj.query()
            		.filter([["id", "=", product_id]])
            	    .first().then(function(product) {
            	    	$(".oe_product_picture_container").empty();
            	    	if (product){
            	    		if (product.image_medium) {
	            	    		var $item = $(QWeb.render("ProductPictureResult", {product: product}));  
	            	    		$(".oe_product_picture_container").append($item);
	                            //self.$el.append($item);
            	    		}
            	    	};
            	});
            };
            function picture_pattern_render(pattern_id){        
            	var pattern_obj = new instance.web.Model("ineco.pattern");
            	pattern_obj.query()
            		.filter([["id", "=", pattern_id]])
            	    .first().then(function(pattern) {
            	    	$(".oe_pattern_picture_container").empty();
            	    	if (pattern){
            	    		if (pattern.image_medium) {
	            	    		var $item = $(QWeb.render("PatternPictureResult", {pattern: pattern}));  
	            	    		$(".oe_pattern_picture_container").append($item);
	                            //self.$el.append($item);
            	    		}
            	    	};
            	});
            };
            function picture_hr_render(pattern_id){        
            	var pattern_obj = new instance.web.Model("hr.employee");
            	pattern_obj.query()
            		.filter([["id", "=", pattern_id]])
            	    .first().then(function(pattern) {
            	    	$(".oe_hr_picture_container").empty();
            	    	if (pattern){
            	    		if (pattern.image_medium) {
	            	    		var $item = $(QWeb.render("HRPictureResult", {hr: pattern}));  
	            	    		$(".oe_hr_picture_container").append($item);
	                            //self.$el.append($item);
            	    		}
            	    	};
            	});
            };
            function lot_append(model_id, id) {
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var lotResult = new instance.ineco_barcode.LotResult(this);
		                        lotResult.appendTo($(".oe_barcode_homepage_right"));
		                        if (result2.ref) {
		                        	$(".oe_lot_code").text(result2.name + '/' + result2.ref) ;
		                        }
		                        else {
		                        	$(".oe_lot_code").text(result2.name) ;
		                        };
		                        $(".oe_lot_quantity").text(result2.stock_available) ;
		                        location_lot_render(id) ;
		                        new instance.web.Model('ir.model').query(["id"]).filter([['model','=','product.product']]).first().done(function(model_product){
		                        	var model_product_id = model_product.id;
			                        product_append(model_product_id, result2.product_id[0]) ;
		                        });
		                	}
	                		else {
	                			$(".oe_lot_code").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_lot_code").text('Model Not Found!');
                   	};
                });
            };
            function product_append(model_id, id){
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var productResult = new instance.ineco_barcode.ProductResult(this);
		                        productResult.appendTo($(".oe_barcode_homepage_right"));
		                        $(".oe_product_id").text(id) ;
		                        $(".oe_product_name").text(result2.name) ;
		                        $(".oe_product_unit").text(result2.uom_id[1]) ;
		                        $(".oe_product_default_code").text((result2.default_code || '')) ;
		                        $(".oe_product_onhand").text(Math.round(result2.qty_available).toLocaleString()) ;
		                        location_render(id);
		                        supplier_render(id);
		                        last_purchase_render(id);
		                        cost_render(id);
		                        picture_render(id);
		                	}
	                		else {
	                			$(".oe_barcode_result").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_barcode_result").text('Model Not Found!');
                   	};
                });            	
            };
            function pattern_line_append(model_id, id) {
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var lineResult = new instance.ineco_barcode.PatternLineResult(this);
		                        lineResult.appendTo($(".oe_barcode_homepage_right"));
		                        $(".oe_patternline_name").text(result2.type_id[1]) ;
		                        new instance.web.Model('ir.model').query(["id"]).filter([['model','=','ineco.pattern']]).first().done(function(model_product){
		                        	var model_pattern_id = model_product.id;
			                        pattern_append(model_pattern_id, result2.pattern_id[0]) ;
		                        });
		                	}
	                		else {
	                			$(".oe_patternline_name").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_patternline_name").text('Model Not Found!');
                   	};
                });
            };
            function pattern_append(model_id, id){
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var patternResult = new instance.ineco_barcode.PatternResult(this);
		                        patternResult.appendTo($(".oe_barcode_homepage_right"));
		                        //console.log(result2);
		                        $(".oe_pattern_id").text(result2.id) ;
		                        $(".oe_pattern_name").text(result2.name) ;
		                        $(".oe_pattern_saleorder").text(result2.saleorder_id[1]) ;
		                        $(".oe_pattern_garmentorder").text(result2.garment_order_no) ;
		                        $(".oe_pattern_customer").text(result2.partner_id[1]) ;
		                        $(".oe_pattern_employee").text(result2.employee_id[1]) ;
		                        $(".oe_pattern_sampling").text(result2.sampling_order_no) ;
		                        $(".oe_pattern_mastermo").text(result2.garment_order_no_org || '') ;
		                        $(".oe_pattern_producttype").text(result2.product_type_id[1]) ;
		                        $(".oe_pattern_location").text(result2.location_id[1]) ;
		                        $(".oe_pattern_sale").text(result2.user_id[1]) ;
		                        picture_pattern_render(id);
		                	}
	                		else {
	                			$(".oe_barcode_result").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_barcode_result").text('Model Not Found!');
                   	};
                });            	
            };
            function hr_append(model_id, id){
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var hrResult = new instance.ineco_barcode.HRResult(this);
		                        hrResult.appendTo($(".oe_barcode_homepage_right"));
		                        //console.log(result2);
		                        $(".oe_hr_id").text(result2.id) ;
		                        $(".oe_hr_code").text(result2.otherid) ;
		                        $(".oe_hr_name").text(result2.name_related) ;
		                        $(".oe_hr_job_name").text(result2.job_id[1]) ;
		                        $(".oe_hr_department_name").text(result2.department_id[1]) ;
		                        $(".oe_hr_manager_name").text(result2.parent_id[1]) ;
		                        picture_hr_render(id);
		                	}
	                		else {
	                			$(".oe_barcode_result").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_barcode_result").text('Model Not Found!');
                   	};
                });            	
            };
            function mrp_component_append(model_id, id) {
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var lineResult = new instance.ineco_barcode.FGLineResult(this);
		                        lineResult.appendTo($(".oe_barcode_homepage_right"));
		                        $(".oe_fg_component_name").text(result2.type_id[1]) ;
		                        new instance.web.Model('ir.model').query(["id"]).filter([['model','=','mrp.production']]).first().done(function(model_product){
		                        	var model_pattern_id = model_product.id;
			                        mrp_append(model_pattern_id, result2.production_id[0]) ;
		                        });
		                	}
	                		else {
	                			$(".oe_fg_component_name").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_fg_component_name").text('Model Not Found!');
                   	};
                });
            };
            function mrp_append(model_id, id){
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var webResult = new instance.ineco_barcode.FGResult(this);
		                        webResult.appendTo($(".oe_barcode_homepage_right"));
		                        //console.log(result2);
		                        $(".oe_mrp_id").text(result2.id) ;
		                        $(".oe_mrp_code").text(result2.name) ;
		                        //$(".oe_mrp_customer_name").text(result2.sale_order_id[1]) ;
		                        $(".oe_mrp_date").text(result2.date_planned) ;
		                        $(".oe_mrp_date_delivery").text(result2.name) ;
		                        $(".oe_mrp_type").text(result2.bill_type || '') ;
		                        $(".oe_mrp_bill").text(result2.bill_no || '') ;
		                        $(".oe_mrp_worker").text(result2.worker || '') ;
		                        $(".oe_mrp_comment").text(result2.commnent || '') ;
		                        $(".oe_mrp_size").text(result2.size_id[1] || '') ;
		                        $(".oe_mrp_color").text(result2.color_id[1] || '') ;
		                        $(".oe_mrp_gender").text(result2.gender_id[1] || '') ;
		                        $(".oe_mrp_note").text(result2.note  || '') ;
		                        $(".oe_mrp_total").text(result2.product_qty) ;
		                        //$(".oe_mrp_grand_total").text(result2.name) ;
		                        $(".oe_mrp_product").text(result2.product_id[1]) ;
		                        $(".oe_mrp_pattern").text(result2.pattern_id[1]) ;
		                        render_customer_by_saleorder(result2.sale_order_id[0]) ;
		                        render_deliverydate_by_saleorder(result2.sale_order_id[0]) ;
		                        picture_pattern_render(result2.pattern_id[0]) ;
		                        render_mrp_grandtotal(result2.origin || false) ;
		                	}
	                		else {
	                			$(".oe_barcode_result").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_barcode_result").text('Model Not Found!');
                   	};
                });            	
            };
            function saleorder_append(model_id, id){
                new instance.web.Model("ir.model").query(["model"]).filter([["id", "=", model_id]]).first().then(function(result) {
                   	if (result) {
                   		model = result.model;
 	                	new instance.web.Model(model).query().filter([["id", "=", id]]).first().then(function(result2) {
	                		if (result2) {		                    	
		                        var hrResult = new instance.ineco_barcode.SaleOrderResult(this);
		                        hrResult.appendTo($(".oe_barcode_homepage_right"));
		                        //console.log(result2);
		                        $(".oe_saleorder_id").text(result2.id) ;
		                        $(".oe_sale_code").text(result2.name) ;
		                        $(".oe_sale_garment_order_no").text(result2.garment_order_no) ;
		                        $(".oe_sale_date_order").text(result2.date_order) ;
		                        $(".oe_sale_date_garment").text(result2.garment_order_date) ;
		                        $(".oe_sale_date_delivery").text(result2.date_delivery) ;
		                        $(".oe_sale_customer").text(result2.partner_id[1]) ;
		                        $(".oe_sale_name").text(result2.user_id[1]) ;
		                        $(".oe_sale_employee_pattern").text(result2.employee_id[1]) ;
		                        $(".oe_sale_employee_pattern_finish").text(result2.date_pattern_finish.substring(0,10) || '') ;
		                        $(".oe_sale_employee_sampling").text(result2.sampling_marker || '') ;
		                        $(".oe_sale_employee_sampling_finish").text(result2.sampling_marker_finish && result2.sampling_marker_finish.substring(0,10) || '') ;
		                        $(".oe_sale_employee_cut").text(result2.sampling_employee1 && result2.sampling_employee1 || '') ;
		                        $(".oe_sale_employee_cut_finish").text(result2.sampling_employee1_finish && result2.sampling_employee1_finish.substring(0,10) || '') ;
		                        $(".oe_sale_employee_sew").text(result2.sampling_employee2 && result2.sampling_employee2 || '') ;
		                        $(".oe_sale_employee_sew_finish").text(result2.sampling_employee2_finish && result2.sampling_employee2_finish.substring(0,10) || '') ;
		                        render_product_by_saleorder(result2.id) ;
		                        render_productqty_by_saleorder(result2.id) ;
		                	}
	                		else {
	                			$(".oe_barcode_result").text('Not Found!');
	                		} ;
	                	}) ;
                	}
                   	else {
                   		$(".oe_barcode_result").text('Model Not Found!');
                   	};
                });            	
            };
            switch (e.which) {
            case $.ui.keyCode.ENTER:      
            	var code = $(".oe_barcode_search").val() ;
            	var result = code.split(":");
            	var id = result[0];
            	var model_id = result[1];
            	var model ;
            	var out_text ;
            	$(".oe_barcode_homepage_right").empty();
            	if (result.length == 1){
                    new instance.web.Model('ir.model').query(["id"]).filter([['model','=','stock.production.lot']]).first().done(function(model_lot){
                    	var model_production_lot_id = model_lot.id;
                    	lot_append(model_production_lot_id, result[0]) ;    
                    }) ;
            	} else if (result.length == 2){
                    new instance.web.Model('ir.model').query(["id"]).filter([['model','=','product.product']]).first().done(function(model_product){
                    	var model_product_id = model_product.id;
                        new instance.web.Model('ir.model').query(["id"]).filter([['model','=','stock.production.lot']]).first().done(function(model_lot){
                        	var model_production_lot_id = model_lot.id;
                            new instance.web.Model('ir.model').query(["id"]).filter([['model','=','ineco.pattern']]).first().done(function(model_pattern){
                            	var model_pattern = model_pattern.id;
                            	new instance.web.Model('ir.model').query(["id"]).filter([['model','=','ineco.pattern.line']]).first().done(function(model_pattern_line){
                            		var model_pattern_line_id = model_pattern_line.id;
                                	new instance.web.Model('ir.model').query(["id"]).filter([['model','=','hr.employee']]).first().done(function(hr_employee){
                                		var model_employee_id = hr_employee.id;
                                    	new instance.web.Model('ir.model').query(["id"]).filter([['model','=','mrp.production']]).first().done(function(mrp_production){
                                    		var model_production_id = mrp_production.id;
                                        	new instance.web.Model('ir.model').query(["id"]).filter([['model','=','ineco.mrp.pattern.component']]).first().done(function(ineco_component){
                                        		var model_component_id = ineco_component.id;
                                            	new instance.web.Model('ir.model').query(["id"]).filter([['model','=','sale.order']]).first().done(function(sale_order){
                                            		var model_sale_id = sale_order.id;
                                            		if (model_id == model_product_id) {         
                                                		product_append(model_id, id) ;  		
                                                	}
                                                	else if (model_id == model_pattern) {
                                                		pattern_append(model_id, id) ;
                                                	}
                                                	else if (model_id == model_pattern_line_id) {
                                                		pattern_line_append(model_pattern_line_id, id) ;
                                                	}
                                                	else if (model_id == model_production_lot_id) {
                                                		lot_append(model_id, id) ;
                                                	}
                                                	else if (model_id == model_production_id) {
                                                		mrp_append(model_id, id) ;
                                                	}
                                                	else if (model_id == model_component_id) {
                                                		mrp_component_append(model_id, id) ;
                                                	}
                                                	else if (model_id == model_sale_id) {
                                                		saleorder_append(model_id, id) ;
                                                	}
                                                	else if (model_id == model_employee_id) {
                                                		hr_append(model_id, id) ;
                                                	} ;
                                            	});
                                        	});                                    		
                                    	});                                 	
                                	});
                            	});
                            }) ;
                        });
                    });
            	};
                $(".oe_barcode_search").val("");
                $(".oe_barcode_search").focus();
                break;
            }
        },
    });

    instance.ineco_barcode.BarcodeResult = instance.web.Widget.extend({
        template: "BarcodeResult",
        start: function() {
            var self = this;
        },
    });

    instance.ineco_barcode.ProductResult = instance.web.Widget.extend({
        template: "ProductResult",
        start: function() {
            var self = this;
            this.$el.on('click', 'a.oe_goto_product', this.do_click_product);
        },
        do_click_product: function(ev) {
        	//ev.preventDefault();
        	var product_id = $(".oe_product_id").text() ;
        	var ts = new Date().getTime();
            var return_url = _.str.sprintf('%s//%s/?ts=%s#id=%s&view_type=form&model=product.product', location.protocol, location.host, ts, product_id );
            window.open(return_url);
            //window.location = return_url;
        },
    });

    instance.ineco_barcode.LotResult = instance.web.Widget.extend({
        template: "LotResult",
        start: function() {
            var self = this;
        },
    });

    instance.ineco_barcode.PatternResult = instance.web.Widget.extend({
        template: "PatternResult",
        start: function() {
            var self = this;
            this.$el.on('click', 'a.oe_goto_pattern', this.do_click_pattern);
        },
        do_click_pattern: function(ev) {
        	//ev.preventDefault();
        	var pattern_id = $(".oe_pattern_id").text() ;
        	var ts = new Date().getTime();
            var return_url = _.str.sprintf('%s//%s/?ts=%s#id=%s&view_type=form&model=ineco.pattern', location.protocol, location.host, ts, pattern_id );
            window.open(return_url);
            //window.location = return_url;
        },
    });
    
    instance.ineco_barcode.PatternLineResult = instance.web.Widget.extend({
        template: "PatternLineResult",
        start: function() {
            var self = this;
        },
    });
    
    instance.ineco_barcode.ProductPictureResult = instance.web.Widget.extend({
        template: "ProductPictureResult",
        start: function() {
            var self = this;
        },
    });
    
    instance.ineco_barcode.PatternPictureResult = instance.web.Widget.extend({
        template: "PatternPictureResult",
        start: function() {
            var self = this;
        },
    });

    instance.ineco_barcode.HRResult = instance.web.Widget.extend({
        template: "HRResult",
        start: function() {
            var self = this;
            this.$el.on('click', 'a.oe_goto_hr', this.do_click_hr);
        },
        do_click_hr: function(ev) {
        	var hr_id = $(".oe_hr_id").text() ;
        	var ts = new Date().getTime();
            var return_url = _.str.sprintf('%s//%s/?ts=%s#id=%s&view_type=form&model=hr.employee', location.protocol, location.host, ts, hr_id );
            window.open(return_url);
        },
    });

    instance.ineco_barcode.HRPictureResult = instance.web.Widget.extend({
        template: "HRPictureResult",
        start: function() {
            var self = this;
        },
    });

    instance.ineco_barcode.FGLineResult = instance.web.Widget.extend({
        template: "FGLineResult",
        start: function() {
            var self = this;
        },
    });

    instance.ineco_barcode.FGResult = instance.web.Widget.extend({
        template: "FGResult",
        start: function() {
            var self = this;
            this.$el.on('click', 'a.oe_goto_fg', this.do_click_fg);
        },
        do_click_fg: function(ev) {
        	var id = $(".oe_mrp_id").text() ;
        	var ts = new Date().getTime();
            var return_url = _.str.sprintf('%s//%s/?ts=%s#id=%s&view_type=form&model=mrp.production', location.protocol, location.host, ts, id );
            window.open(return_url);
        },
    });

    instance.ineco_barcode.SaleOrderResult = instance.web.Widget.extend({
        template: "SaleOrderResult",
        start: function() {
            var self = this;
            this.$el.on('click', 'a.oe_goto_saleorder', this.do_click_saleorder);
        },
        do_click_saleorder: function(ev) {
        	var id = $(".oe_saleorder_id").text() ;
        	var ts = new Date().getTime();
            var return_url = _.str.sprintf('%s//%s/?ts=%s#id=%s&view_type=form&model=sale.order', location.protocol, location.host, ts, id );
            window.open(return_url);
        },
    });

}