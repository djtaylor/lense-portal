cs.import('CSNetworkRoutersList', function() { 
	
	/**
	 * Target Router
	 */
	this.router = function() {
		return $('input[type="hidden"][name="router_uuid"]').val();
	}
	
	/**
	 * Callback: Delete Router
	 */
	cs.register.method('router.delete', function(c,m,d,a) {
		if (c == 200) {
			cs.layout.remove('div[type="row"][target="routers"][router="' + d.uuid + '"]');
		}
	});
	
	/**
	 * Callback: Create Router
	 */
	cs.register.callback('router.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][table="routers_list"]').append(cs.layout.create.element('div', {
				css:  'table_row',
				attr: {
					target: 'routers',
					router: d.uuid
				},
				children: [
				    cs.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [cs.layout.create.element('input', {
				    		attr: {
				    			type: 'radio',
				    			name: 'router_uuid',
				    			value: d.uuid,
				    			action: 'update'
				    		}
				    	})]
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col table_link',
				    	attr: {
				    		type: 'button',
				    		action: 'link',
				    		target: 'network?panel=routers&router=' + d.uuid,
				    		col: 'router_name'
				    	},
				    	text: d.name
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'router_uuid'
				    	},
				    	text: d.uuid
				    }),
				    cs.layout.create.element('div', {
				    	css: (d.hasOwnProperty('datacenter')) ? 'table_col table_link' : 'table_col',
				    	attr: (function() {
				    		if (d.hasOwnProperty('datacenter')) {
				    			return {
				    				type: 'button',
				    				action: 'link',
				    				target: 'admin?panel=datacenters&datacenter' + d.datacenter.uuid,
				    				col: 'router_datacenter'
				    			}
				    		} else {
				    			return {
				    				col: 'router_datacenter'
				    			};
				    		}
				    	})(),
				    	text: (d.hasOwnProperty('datacenter')) ? d.datacenter.name : ''
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'router_interfaces'
				    	},
				    	text: $(d.interfaces).length
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'router_desc'
				    	},
				    	text: d.desc
				    })
				]
			}));
			
			// Refresh the layout
			cs.layout.refresh();
		}
	});
	
	/**
	 * Method: Delete Router
	 */
	cs.register.method('router.delete', function() {
		cs.layout.popup_toggle(false, 'router.delete', false, function() { 
			cs.layout.loading(true, 'Deleting router...', function() {
				cs.api.request.post({
					path: 'network/router',
					action: 'delete',
					_data: {
						uuid: cs.network.router();
					},
					callback: {
						id: 'router.delete'
					}
				});
			});
		});
	});
	
	/**
	 * Method: Create Router
	 */
	cs.register.method('router.create', function() {
		cs.layout.popup_toggle(false, 'router.create', false, function() { 
			cs.layout.loading(true, 'Creating router...', function() {
				cs.api.request.post({
					path: 'network/router',
					action: 'delete',
					_data: (function() {
						
						// Request data
						var _data = {};
						$('input[type="text"][form="create_router"]').each(function(i,e) {
							var attr = get_attr(e);
							_data[attr.name] = $(e).val();
						});
						
						// If setting a datacenter
						var datacenter = $('select[form="create_router"][name="datacenter"]').val();
						if (defined(datacenter)) {
							_data['datacenter'] = datacenter;
						}
						
						// Return the request data
						return _data;
					})(),
					callback: {
						id: 'router.create'
					}
				});
			});
		});
	});
});