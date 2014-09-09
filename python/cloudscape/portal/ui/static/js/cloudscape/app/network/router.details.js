cs.import('CSNetworkRouterDetails', function() { 
	
	// Active router
	this.active = cs.url.param_get('router');
	
	/**
	 * Initialize: CSNetworkRouterDetails
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			$('.table_50').animate({
				opacity: '1.0'
			}, 500);
		});
	}
	
	/**
	 * Callback: Save Router
	 */
	cs.register.callback('router.save', function(c,m,d,a) {
		
		// Switch the edit/save buttons
		$('div[type="button"][target="router.save"]').css('display', 'none').attr('active', 'no');
		$('div[type="button"][target="router.edit"]').css('display', 'block').attr('active', 'yes');
		
		// Enable the form fields
		$('input[type="text"][form="edit_router"]').attr('disabled', '');
		$('select[form="edit_router"]').attr('disabled', '');
	});
	
	/**
	 * Callback: Remove Interface
	 */
	cs.register.callback('router.remove_interface', function(c,m,d,a) {
		if (c == 200) {
			cs.layout.remove('div[type="toggle"][name="' + d.uuid + '_attrs"]');
			cs.layout.remove('div[interface="' + d.uuid + '"]');
			$('input[type="hidden"][name="interface_uuid"]').val('');
		}
	});
	
	/**
	 * Callback: Add Interface
	 */
	cs.register.callback('router.add_interface', function(c,m,d,a) {
		if (c == 200) {
			
			// Create the parent row
			$('div[type="table"][name="router_interfaces"]').append(cs.layout.create.element('div', {
				css: 'table_row table_row_link',
				attr: (function() {
					_attr = {
						type: 'button',
						action: 'toggle',
						target: d.uuid + '_attrs'
					};
					_attr['interface'] = d.uuid;
					return _attr;
				})(),
				children: [
				    cs.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [cs.layout.create.element('input', {
				    		attr: {
				    			type: 'radio',
				    			name: 'interface_uuid',
				    			action: 'update',
				    			value: d.uuid
				    		}
				    	})]
				    }),     
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'interface_name'
				    	},
				    	text: d.name
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'interface_uuid'
				    	},
				    	text: d.uuid
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'interface_desc'
				    	},
				    	text: d.desc
				    })
				]
			}));
			
			// Create the attributes group
			$('div[type="table"][name="router_interfaces"]').append(cs.layout.create.element('div', {
				css: 'table_row_group',
				attr: {
					style: 'display:none;',
					type: 'toggle',
					name: d.uuid + '_attrs'
				},
				children: [
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [
				    	    cs.layout.create.element('div', {
				    	    	css: 'table_row_label',
				    	    	text: 'Name'
				    	    }),
				    	    cs.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [cs.layout.create.element('input', {
						    		attr: {
						    			type: 'text',
						    			form: 'edit_interface_' + d.uuid,
						    			name: 'name',
						    			value: d.name,
						    			disabled: ''
						    		}
						    	})]
						    })
				    	]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [
				    	    cs.layout.create.element('div', {
				    	    	css: 'table_row_label',
				    	    	text: 'Description'
				    	    }),
				    	    cs.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [cs.layout.create.element('input', {
						    		attr: {
						    			type: 'text',
						    			form: 'edit_interface_' + d.uuid,
						    			name: 'desc',
						    			value: d.desc,
						    			disabled: ''
						    		}
						    	})]
						    })
				    	]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [
				    	    cs.layout.create.element('div', {
				    	    	css: 'table_row_label',
				    	    	text: 'HW Address'
				    	    }),
				    	    cs.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [cs.layout.create.element('input', {
						    		attr: {
						    			type: 'text',
						    			form: 'edit_interface_' + d.uuid,
						    			name: 'hwaddr',
						    			value: d.hwaddr,
						    			disabled: ''
						    		}
						    	})]
						    })
				    	]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [
				    	    cs.layout.create.element('div', {
				    	    	css: 'table_row_label',
				    	    	text: 'IPv4 Address'
				    	    }),
				    	    cs.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [cs.layout.create.element('input', {
						    		attr: {
						    			type: 'text',
						    			form: 'edit_interface_' + d.uuid,
						    			name: 'ipv4_addr',
						    			value: (d.ipv4_addr) ? d.ipv4_addr : '',
						    			disabled: ''
						    		}
						    	})]
						    })
				    	]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [ 
				    	    cs.layout.create.element('div', {
				    	    	css: 'table_row_label',
				    	    	text: 'IPv4 Network'
				    	    }),
				    	    cs.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [cs.layout.create.element('select', {
						    		attr: {
						    			form: 'edit_interface_' + d.uuid,
						    			name: 'ipv4_net',
						    			disabled: ''
						    		},
						    		children: (function() {
						    			
						    			var _c = [cs.layout.create.element('option', {
						    				attr: (function() {
						    					var _attr = {
						    						value: ''	
						    					};
						    					if (!defined(d.ipv4_net)) {
						    						_attr['selected'] = 'selected';
						    					}
						    					return _attr;
						    				})(),
						    				text: '-none-'
						    			})];
						    			
						    			$.each($('#ipv4_networks').find('network'), function(i,e) {
						    				var ea = get_attr(e);
						    				_c.push(cs.layout.create.element('option', {
						    					attr: (function() {
						    						var _attr = {
						    							value: ea.uuid
						    						};
						    						if (d.ipv4_net == ea.uuid) {
						    							_attr['selected'] = 'selected';
						    						}
						    						return _attr;
						    					})(),
						    					text: ea.label
						    				}));
						    			});
						    			
						    			return _c;
						    		})()
						    	})]
						    })
					    ]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [
				    	    cs.layout.create.element('div', {
				    	    	css: 'table_row_label',
				    	    	text: 'IPv6 Address'
				    	    }),
				    	    cs.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [cs.layout.create.element('input', {
						    		attr: {
						    			type: 'text',
						    			form: 'edit_interface_' + d.uuid,
						    			name: 'ipv6_addr',
						    			value: (d.ipv6_addr) ? d.ipv6_addr : '',
						    			disabled: ''
						    		}
						    	})]
						    })
				    	]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [ 
				    	    cs.layout.create.element('div', {
				    	    	css: 'table_row_label',
				    	    	text: 'IPv6 Network'
				    	    }),
				    	    cs.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [cs.layout.create.element('select', {
						    		attr: {
						    			form: 'edit_interface_' + d.uuid,
						    			name: 'ipv6_net',
						    			disabled: ''
						    		},
						    		children: (function() {
						    			
						    			var _c = [cs.layout.create.element('option', {
						    				attr: (function() {
						    					var _attr = {
						    						value: ''	
						    					};
						    					if (!defined(d.ipv6_net)) {
						    						_attr['selected'] = 'selected';
						    					}
						    					return _attr;
						    				})(),
						    				text: '-none-'
						    			})];
						    			
						    			$.each($('#ipv6_networks').find('network'), function(i,e) {
						    				var ea = get_attr(e);
						    				_c.push(cs.layout.create.element('option', {
						    					attr: (function() {
						    						var _attr = {
						    							value: ea.uuid
						    						};
						    						if (d.ipv6_net == ea.uuid) {
						    							_attr['selected'] = 'selected';
						    						}
						    						return _attr;
						    					})(),
						    					text: ea.label
						    				}));
						    			});
						    			
						    			return _c;
						    		})()
						    	})]
						    })
					    ]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_row',
				    	children: [cs.layout.create.element('div', {
				    		css: 'table_row_actions',
				    		children: [
				    		    cs.layout.create.element('div', {
				    		    	css: 'table_action',
				    		    	attr: {
				    		    		active: 'yes',
				    		    		type: 'button',
				    		    		action: 'method',
				    		    		target: 'interface.edit',
				    		    		arg: d.uuid
				    		    	},
				    		    	text: 'Edit'
				    		    }),
				    		    cs.layout.create.element('div', {
				    		    	css: 'table_action',
				    		    	attr: {
				    		    		active: 'no',
				    		    		type: 'button',
				    		    		action: 'method',
				    		    		target: 'interface.save',
				    		    		arg: d.uuid,
				    		    		style: 'display:none;'
				    		    	},
				    		    	text: 'Save'
				    		    })
				    		]
				    	})]
				    })
				]
			}));
			
			// Refresh the layout
			cs.layout.refresh();
		}
	});
	
	/**
	 * Callback: Save Interface
	 */
	cs.register.callback('interface.save', function(c,m,d,a) {
		
		// Switch the edit/save buttons
		$('div[type="button"][target="interface.edit"][arg="' + a.uuid + '"]').css('display', 'block').attr('active', 'yes');
		$('div[type="button"][target="interface.save"][arg="' + a.uuid + '"]').css('display', 'none').attr('active', 'no');
		
		// Enable the form fields
		$('input[type="text"][form="edit_interface_' + a.uuid + '"]').attr('disabled', '');
		$('select[form="edit_interface_' + a.uuid + '"]').attr('disabled', '');
		
		// If the request succeeded
		if (c == 200) {
			$('div[interface="' + a.uuid + '"]').find('div[col="interface_name"]').text($('input[type="text"][form="edit_interface_' + a.uuid + '"][name="name"]').val());
			$('div[interface="' + a.uuid + '"]').find('div[col="interface_desc"]').text($('input[type="text"][form="edit_interface_' + a.uuid + '"][name="desc"]').val());
		}
	});
	
	/**
	 * Method: Save Router
	 */
	cs.register.method('router.save', function() {
		cs.layout.loading(true, 'Updating router...', function() {
			cs.api.request.post({
				path: 'network/router',
				action: 'update',
				_data: (function() {
					
					// Request data
					var _data = {};
					$('input[type="text"][form="edit_router"]').each(function(i,e) {
						var attr = get_attr(e);
						var val = $(e).val();
						_data[attr.name] = (defined(val)) ? val : null;
					});
					
					// Datacenter
					var datacenter = $('select[form="edit_router"][name="datacenter"]').val();
					_data['datacenter'] = (defined(datacenter)) ? datacenter : null;
					
					// IPv4 Block
					var ipv4_net = $('select[form="edit_router"][name="ipv4_net"]').val();
					_data['ipv4_net'] = (defined(ipv4_net)) ? ipv4_net : null;
					
					// IPv6 Block
					var ipv6_net = $('select[form="edit_router"][name="ipv6_net"]').val();
					_data['ipv6_net'] = (defined(ipv6_net)) ? ipv6_net : null;
					
					// Return the request data
					return _data;
				})(),
				callback: {
					id: 'router.save'
				}
			});
		});
	});
	
	/**
	 * Method: Edit Router
	 */
	cs.register.method('router.edit', function() {
		
		// Switch the edit/save buttons
		$('div[type="button"][target="router.edit"]').css('display', 'none').attr('active', 'no');
		$('div[type="button"][target="router.save"]').css('display', 'block').attr('active', 'yes');
		
		// Enable the form fields
		$('input[type="text"][form="edit_router"]').removeAttr('disabled');
		$('select[form="edit_router"]').removeAttr('disabled');
	});
	
	/**
	 * Method: Save Interface
	 */
	cs.register.method('interface.save', function(i) {
		if (defined(i)) {
			cs.layout.loading(true, 'Updating interface...', function() {
				cs.api.request.post({
					path: 'network/router/interface',
					action: 'update',
					_data: (function() {
						
						// IPv4 address / network
						ipv4_addr = $('input[type="text"][form="edit_interface_' + i + '"][name="ipv4_addr"]').val();
						ipv4_net = $('select[form="edit_interface_' + i + '"][name="ipv4_net"]').val()
						
						// IPv6 address / network
						ipv6_addr = $('input[type="text"][form="edit_interface_' + i + '"][name="ipv6_addr"]').val();
						ipv6_net = $('select[form="edit_interface_' + i + '"][name="ipv6_net"]').val()
						
						// Base data
						var _data = {
							uuid: cs.network.router.active,
							name: $('input[type="text"][form="edit_interface_' + i + '"][name="name"]').val(),
							desc: $('input[type="text"][form="edit_interface_' + i + '"][name="desc"]').val(),
							hwaddr: $('input[type="text"][form="edit_interface_' + i + '"][name="hwaddr"]').val(),
							ipv4_addr: (defined(ipv4_addr)) ? ipv4_addr : null,
							ipv4_net: (defined(ipv4_net)) ? ipv4_net : null,
							ipv6_addr: (defined(ipv6_addr)) ? ipv6_addr : null,
							ipv6_net: (defined(ipv6_net)) ? ipv6_net : null
						}
						
						// Set the target interface
						_data['interface'] = i;
						
						// Return the request data
						return _data;
						
					})(),
					callback: {
						id: 'interface.save',
						args: {
							uuid: i
						}
					}
				});
			});
		}
	});
	
	/**
	 * Method: Edit Interface
	 */
	cs.register.method('interface.edit', function(i) {
		if (defined(i)) {
			
			// Switch the edit/save buttons
			$('div[type="button"][target="interface.edit"][arg="' + i + '"]').css('display', 'none').attr('active', 'no');
			$('div[type="button"][target="interface.save"][arg="' + i + '"]').css('display', 'block').attr('active', 'yes');
			
			// Enable the form fields
			$('input[type="text"][form="edit_interface_' + i + '"]').removeAttr('disabled');
			$('select[form="edit_interface_' + i + '"]').removeAttr('disabled');
		}
	});
	
	/**
	 * Method: Remove Interface
	 */
	cs.register.method('router.remove_interface', function() {
		cs.layout.popup_toggle(false, 'router.remove_interface', false, function() { 
			cs.layout.loading(true, 'Removing router interface...', function() {
				cs.api.request.post({
					path: 'network/router/interface',
					action: 'remove',
					_data: (function() {
						var _d = {
							uuid: cs.network.router.active	
						};
						_d['interface'] = $('input[type="hidden"][name="interface_uuid"]').val();
						return _d;
					})(),
					callback: {
						id: 'router.remove_interface'
					}
				});
			});
		});
	});
	
	/**
	 * Method: Add Interface
	 */
	cs.register.method('router.add_interface', function() {
		cs.layout.popup_toggle(false, 'router.add_interface', false, function() { 
			cs.layout.loading(true, 'Adding router interface...', function() {
				cs.api.request.post({
					path: 'network/router/interface',
					action: 'add',
					_data: (function() {
						
						// Base request data
						_data = {
							name: $('input[form="router_add_interface"][name="name"]').val(),
							desc: $('input[form="router_add_interface"][name="desc"]').val(),
							hwaddr: $('input[form="router_add_interface"][name="hwaddr"]').val(),
							uuid: cs.network.router.active
						}
						
						// IPv4/IPv6 addresses
						var ipv4_addr = $('input[form="router_add_interface"][name="ipv4_addr"]').val();
						var ipv6_addr = $('input[form="router_add_interface"][name="ipv6_addr"]').val();
						if (defined(ipv4_addr)) {
							_data['ipv4_addr'] = ipv4_addr;
						}
						if (defined(ipv6_addr)) {
							_data['ipv6_addr'] = ipv6_addr;
						}
						
						// IPv4/IPv6 networks
						var ipv4_net = $('select[form="router_add_interface"][name="ipv4_net"]').val();
						var ipv6_net = $('select[form="router_add_interface"][name="ipv6_net"]').val();
						if (defined(ipv4_net)) {
							_data['ipv4_net'] = ipv4_net;
						}
						if (defined(ipv6_net)) {
							_data['ipv6_net'] = ipv6_net;
						}
						
						// Return the request data
						return _data;
					})(),
					callback: {
						id: 'router.add_interface'
					}
				});
			});
		});
	});
});