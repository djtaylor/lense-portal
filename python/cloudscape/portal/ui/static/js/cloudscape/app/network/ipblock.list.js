cs.import('CSNetworkIPBlocksList', function() { 
	
	// Protocol / Label
	this.proto = null;
	this.proto_label = null;
	
	// Filtered IP blocks
	this.filtered = {};
	
	/**
	 * Initialize: CSNetworkIPBlocksList
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Protocol and label
		cs.network.ipblock.proto = $('input[type="hidden"][name="protocol"]').val();
		cs.network.ipblock.proto_label = (cs.network.ipblock.proto == 'ipv4') ? 'IPv4' : 'IPv6';
		
		// Block filtering
		cs.network.ipblock.filter();
	}
	
	/**
	 * Filter IP Blocks
	 */
	this.filter = function() {
		
		// Filter keys
		var filter_keys = ['datacenter', 'network.filter']; 
		
		// Get all IP block rows
		var ip_block_rows = $('div[type="row"][target="ip_blocks"]');
		
		// Load all IP blocks
		$.each(ip_block_rows, function(i,ip_block_row) {
			
			// Get the IP block attributes
			var ip_block_attr = get_attr($(ip_block_row).find('attr'));
			
			// Set the IP block filter attributes
			cs.network.ipblock.filtered[ip_block_attr.uuid] = (function() {
				var k = {};
				$.each(filter_keys, function(i,filter_key) {
					k[filter_key] = false;
				});
				return k;
			})();
			
		});
		
		// Refresh filters
		function _refresh() {
			$.each(cs.network.ipblock.filtered, function(ip_block_uuid, ip_block_filters) {
				
				// Look for any active filters
				var filter_enabled = false;
				$.each(ip_block_filters, function(k,v) {
					filter_enabled = (v) ? true : filter_enabled;
				});
				
				// Set the display attribute
				var display = (filter_enabled) ? 'none' : 'block';
				
				// Toggle the IP block element
				$('div[type="row"][target="ip_blocks"][block="' + ip_block_uuid + '"]').css('display', display);
			});
		}
		
		// Wait for filter events
		$('input[target="ipblocks.filter"]').on('change input', function() {
			
			// Get the changed filter element
			var filter_elem = $(this);
			var filter_attr = get_attr(this);
			
			// Text filters
			if (filter_attr.type == 'text') {
				
				// Get the text value
				var ip_filter = filter_elem.val();
				
				// If performing a network search
				if (filter_attr.key == 'network.search') {
					$.each(ip_block_rows, function(i,ip_block_row) {
						
						// Get the IP block attributes element
						var ip_block_attr = get_attr($(ip_block_row).find('attr'));
						
						// If the IP filter box is empty
						if (!defined(ip_filter)) {
							cs.network.ipblock.filtered[ip_block_attr.uuid]['network.filter'] = false;
							
						// Apply the IP filter
						} else {
							cs.network.ipblock.filtered[ip_block_attr.uuid]['network.filter'] = (ip_block_attr.network.indexOf(ip_filter) > -1) ? false : true;
						}
					});
				}
			}
			
			// Checkbox filters
			if (filter_attr.type == 'checkbox') {
				
				// Toggle all elements with the attribute key
				$.each(ip_block_rows, function(i,ip_block_row) {
				
					// Get the IP block attributes element
					var ip_block_attr = get_attr($(ip_block_row).find('attr'));
					
					// If performing a key match
					if ($.inArray(filter_attr.key, ['datacenter']) > -1) {
						if (ip_block_attr[filter_attr.key] == filter_attr.value) {
							cs.network.ipblock.filtered[ip_block_attr.uuid][filter_attr.key] = (filter_elem.is(':checked')) ? false : true;
						}
					}
				});
			}
			
			// Refresh filter states
			_refresh();
		});
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
							prefix: parseInt($('input[type="text"][form="ip_block_create"][name="prefix"]').val())
						};
						
						// Description
						var desc = $('input[type="text"][form="ip_block_create"][name="desc"]').val();
						if (defined(desc)) {
							_data['desc'] = desc;
						}
						
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
