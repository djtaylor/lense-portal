cs.import('CSNetworkRoutersList', function() { 
	
	/**
	 * Target Router
	 */
	this.target = function() {
		return $('input[type="hidden"][name="router_uuid"]').val();
	}
	
	/**
	 * Callback: Delete Router
	 */
	cs.register.callback('router.delete', function(c,m,d,a) {
		if (c == 200) {
			
			// Remove the router row
			cs.layout.remove('div[type="row"][target="routers"][router="' + d.uuid + '"]');
		
			// Clear the selected router hidden field
			$('input[type="hidden"][name="router_uuid"]').val('');
		}
	});
	
	/**
	 * Callback: Create Router
	 */
	cs.register.callback('router.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][table="router_list"]').append(cs.layout.create.element('div', {
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
						uuid: cs.network.router.target()
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
					action: 'create',
					_data: (function() {
						
						// Request data
						var _data = {};
						$('input[type="text"][form="router_create"]').each(function(i,e) {
							var attr = get_attr(e);
							var val = $(e).val();
							if (defined(val)) {
								_data[attr.name] = val;
							}
						});
						
						// If setting a datacenter
						var datacenter = $('select[form="router_create"][name="datacenter"]').val();
						if (defined(datacenter)) {
							_data['datacenter'] = datacenter;
						}
						
						// If setting an IPv4 block
						var ipv4_net = $('select[form="router_create"][name="ipv4_net"]').val();
						if (defined(ipv4_net)) {
							_data['ipv4_net'] = ipv4_net;
						}
						
						// If setting an IPv6 block
						var ipv6_net = $('select[form="router_create"][name="ipv6_net"]').val();
						if (defined(ipv6_net)) {
							_data['ipv6_net'] = ipv6_net;
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