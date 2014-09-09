cs.import('CSNetworkIPBlocksList', function() { 
	
	// Protocol / Label
	this.proto = null;
	this.proto_label = null;
	
	/**
	 * Initialize: CSNetworkIPBlocksList
	 * @constructor
	 */
	this.__init__ = function() {
		cs.network.ipblock.proto = $('input[type="hidden"][name="protocol"]').val();
		cs.network.ipblock.proto_label = (cs.network.ipblock.proto == 'ipv4') ? 'IPv4' : 'IPv6';
	}
	
	/**
	 * Callback: Delete IP Block
	 */
	cs.register.callback('ip_block.delete', function(c,m,d,a) {
		if (c == 200) {
			cs.layout.remove('div[type="row"][target="ip_blocks"][block="' + d.uuid + '"]');
			$('input[type="hidden"][name="ip_block_uuid"]').val('');
		}
	});
	
	/**
	 * Callback: Create IP Block
	 */
	cs.register.callback('ip_block.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][table="ip_block_list"]').append(cs.layout.create.element('div', {
				css: 'table_row',
				attr: {
					type: 'row',
					target: 'ip_blocks',
					block: d.uuid
				},
				children: [
					cs.layout.create.element('div', {
						css: 'table_select_col',
						children: [cs.layout.create.element('input', {
							attr: {
								type: 'radio',
								name: 'ip_block_uuid',
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
				    		target: 'network?panel=' + cs.network.ipblock.proto + 'blocks&block=' + d.uuid,
				    		col: 'ip_block_network'
				    	},
				    	text: d.network
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'ip_block_prefix'
				    	},
				    	text: d.prefix
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'ip_block_desc'
				    	},
				    	text: d.desc
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'ip_block_uuid'
				    	},
				    	text: d.uuid
				    }),
				    cs.layout.create.element('div', {
				    	css:  (d.hasOwnProperty('datacenter')) ? 'table_col table_link' : 'table_col',
				    	attr: (function() {
				    		if (d.hasOwnProperty('datacenter')) {
				    			return {
				    				col: 'ip_block_datacenter',
				    				type: 'button',
				    				action: 'link',
				    				target: 'admin?panel=datacenters&datacenter=' + d.datacenter.uuid
				    			}
				    		} else {
				    			return {
				    				col: 'ip_block_datacenter'
				    			}
				    		}
				    	})(),
				    	text: (d.hasOwnProperty('datacenter')) ? d.datacenter.name : ''
				    }),
				    cs.layout.create.element('div', {
				    	css:  (d.hasOwnProperty('router')) ? 'table_col table_link' : 'table_col',
				    	attr: (function() {
				    		if (d.hasOwnProperty('router')) {
				    			return {
				    				col: 'ip_block_router',
				    				type: 'button',
				    				action: 'link',
				    				target: 'network?panel=routers&router=' + d.router.uuid
				    			}
				    		} else {
				    			return {
				    				col: 'ip_block_router'
				    			}
				    		}
				    	})(),
				    	text: (d.hasOwnProperty('router')) ? d.router.name : ''
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'ip_block_active'
				    	},
				    	text: (d.active) ? 'True' : 'False'
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'ip_block_locked'
				    	},
				    	text: (d.locked) ? 'True' : 'False'
				    })
				]
			}));
			
			// Refresh the layout
			cs.layout.refresh();
		}
	});
	
	/**
	 * Method: Delete IP Block
	 */
	cs.register.method('ip_block.delete', function() {
		cs.layout.loading(true, 'Deleting ' + cs.network.ipblock.proto_label + ' block...', function() {
			cs.api.request.post({
				path: 'network/block/' + cs.network.ipblock.proto,
				action: 'delete',
				_data: {
					uuid: $('input[type="hidden"][name="ip_block_uuid"]').val()
				},
				callback: {
					id: 'ip_block.delete'
				}
			});
		});
	});
	
	/**
	 * Method: Create IP Block
	 */
	cs.register.method('ip_block.create', function() {
		cs.layout.popup_toggle(false, 'ip_block.create', false, function() { 
			cs.layout.loading(true, 'Creating ' + cs.network.ipblock.proto_label + ' block...', function() {
				cs.api.request.post({
					path: 'network/block/' + cs.network.ipblock.proto,
					action: 'create',
					_data: (function() {
						
						// Request data
						var _data = {
							network: $('input[type="text"][form="ip_block_create"][name="network"]').val(),
							prefix: parseInt($('input[type="text"][form="ip_block_create"][name="prefix"]').val()),
							desc: $('input[type="text"][form="ip_block_create"][name="desc"]').val()
						};
						
						// Active/locked
						_data['active'] = ($('input[form="ip_block_create"][name="active"]').is(':checked')) ? true : false;
						_data['locked'] = ($('input[form="ip_block_create"][name="locked"]').is(':checked')) ? true : false;
						
						// If setting a datacenter
						var datacenter = $('select[form="ip_block_create"][name="datacenter"]').val();
						if (defined(datacenter)) {
							_data['datacenter'] = datacenter;
						}
						
						// If setting a router
						var router = $('select[form="ip_block_create"][name="router"]').val();
						if (defined(router)) {
							_data['router'] = router;
						}
						
						// Return the request data
						return _data;
					})(),
					callback: {
						id: 'ip_block.create'
					}
				});
			});
		});
	});
});
