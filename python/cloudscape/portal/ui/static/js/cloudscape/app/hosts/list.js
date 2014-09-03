/**
 * CloudScape Hosts List
 */
cs.import('CSHostsList', function() { 
	
	// Sorted hosts
	this.sorted   = [];
	
	// Filtered hosts
	this.filtered = {};
	
	/**
	 * Initialize: CSHostsList
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Sort hosts menu
		$('select[name="hosts.sort"]').on('change', function() {
			cs.hosts.sort_worker($(this).val());
		});
		
		// Filter hosts
		cs.hosts.filter();
	}
	
	/**
	 * Filter Hosts
	 */
	this.filter = function() {
		
		// Filter keys
		var filter_keys = ['ip.type', 'ip.filter', 'sys', 'datacenter', 'agent_status']; 
		
		// Get all host rows
		var host_rows   = $('div[type="row"][target="hosts"]');
		
		// Load all hosts
		$.each(host_rows, function(i,host_row) {
			
			// Get the host attributes
			var host_attr = get_attr($(host_row).find('attr'));
			
			// Set the hosts filter attributes
			cs.hosts.filtered[host_attr.uuid] = (function() {
				var k = {};
				$.each(filter_keys, function(i,filter_key) {
					k[filter_key] = false;
				});
				return k;
			})();
			
		});
		
		// Refresh filters
		function _refresh() {
			$.each(cs.hosts.filtered, function(host_uuid, host_filters) {
				
				// Look for any active filters
				var filter_enabled = false;
				$.each(host_filters, function(k,v) {
					filter_enabled = (v) ? true : filter_enabled;
				});
				
				// Set the display attribute
				var display = (filter_enabled) ? 'none' : 'block';
				
				// Toggle the host element
				$('div[type="row"][target="hosts"][host="' + host_uuid + '"]').css('display', display);
			});
		}
		
		// Wait for filter events
		$('input[target="hosts.filter"]').on('change input', function() {
			
			// Get the changed filter element
			var filter_elem = $(this);
			var filter_attr = get_attr(this);
			
			// Text filters
			if (filter_attr.type == 'text') {
				
				// Get the text value
				var ip_filter = filter_elem.val();
				
				// If performing an IP search
				if (filter_attr.key == 'ip.search') {
					$.each(host_rows, function(i,host_row) {
						
						// Get the host attributes element
						var host_attr = get_attr($(host_row).find('attr'));
						
						// If the IP filter box is empty
						if (!defined(ip_filter)) {
							cs.hosts.filtered[host_attr.uuid]['ip.filter'] = false;
							
						// Apply the IP filter
						} else {
							cs.hosts.filtered[host_attr.uuid]['ip.filter'] = (host_attr.ip.indexOf(ip_filter) > -1) ? false : true;
						}
					});
				}
			}
			
			// Checkbox filters
			if (filter_attr.type == 'checkbox') {
				
				// Toggle all elements with the attribute key
				$.each(host_rows, function(i,host_row) {
				
					// Get the host attributes element
					var host_attr = get_attr($(host_row).find('attr'));
					
					// If performing a key match
					if ($.inArray(filter_attr.key, ['sys', 'datacenter', 'agent_status']) > -1) {
						if (host_attr[filter_attr.key] == filter_attr.value) {
							cs.hosts.filtered[host_attr.uuid][filter_attr.key] = (filter_elem.is(':checked')) ? false : true;
						}
					}
					
					// If filtering by IP address
					if (filter_attr.key == 'ip') {
						
						// If performing a public/private filter
						if ($.inArray(filter_attr.value, ['public', 'private']) > -1) {
							
							// Set the expected result for the IP type filter
							var expects = (filter_attr.value == 'private') ? true : false;
							
							// Set the filter flag
							if (cs.ipaddr.v4.is_private(host_attr.ip) === expects) {
								cs.hosts.filtered[host_attr.uuid]['ip.type'] = (filter_elem.is(':checked') ? false : true);
							}
						}
					}
				});
			}
			
			// Refresh filter states
			_refresh();
		});
	}
	
	/**
	 * Sort Hosts
	 */
	this.sort_worker = function(k) {
		
		// If not sorting
		if (k == 'none') {
			return true;
		}
		
		// Sort inner
		var sort_inner = {
			ip: function() {
				cs.hosts.sorted.sort(function(a,b) {
					aa = a.key.split(".");
					bb = b.key.split(".");
				    var resulta = aa[0]*0x1000000 + aa[1]*0x10000 + aa[2]*0x100 + aa[3]*1;
				    var resultb = bb[0]*0x1000000 + bb[1]*0x10000 + bb[2]*0x100 + bb[3]*1;
					return resulta-resultb;
				});
			},
			name: function(_s) {
				cs.hosts.sorted.sort(function(a,b) {
					if (a.key < b.key) { return -1; }
					if (a.key > b.key) { return 1;  }
					return 0;
				});
			},
			sys: function(_s) {
				cs.hosts.sorted.sort(function(a,b) {
					if (a.key < b.key) { return -1; }
					if (a.key > b.key) { return 1;  }
					return 0;
				});
			},
			datacenter: function(_s) {
				cs.hosts.sorted.sort(function(a,b) {
					if (a.key < b.key) { return -1; }
					if (a.key > b.key) { return 1;  }
					return 0;
				});
			} 
		}
		
		// Set key value
		function _set_key_value(a) {
			if (k == 'name' || k == 'ip' || k == 'sys' || k == 'datacenter') {
				return a[k];
			} else {
				return a['distro'] + ' ' + a['version'] + ' ' + a['arch'];
			}
		}
		
		// Reset the sorted hosts list
		cs.hosts.sorted = [];
		
		// All hosts / sorted hosts
		var a_hosts = $('div[type="row"][target="hosts"]');
		
		// Process every host row
		$.each(a_hosts, function(i,o) {
			
			// Get the host attributes
			var h_attrs = get_attr($(o).find('attr'));
			
			// Add the host to the list to the sorted
			cs.hosts.sorted.push({
				uuid: h_attrs.uuid,
				key:  _set_key_value(h_attrs),
				elem: o
			});
		});
		
		// Sort the hosts
		sort_inner[k]();
		
		// Update the hosts list
		$('div[type="rows"][target="hosts"]').html((function() {
			var l = '';
			$.each(cs.hosts.sorted, function(i,h) {
				l += cs.layout.html($(h.elem));
			});
			return l;
		})());
	}
	
	/**
	 * Callback: Remove Host
	 */
	cs.register.callback('host.remove', function(c,m,d,a) {
		if (c == 200) {
			cs.layout.remove('div[type$="row"][host$="' + d.uuid + '"]');
		}
	});
	
	/**
	 * Callback: Add Host
	 */
	cs.register.callback('host.add', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][target="hosts"]').prepend(cs.layout.create.element('div', {
				css: 'table_row',
				children: [
				    cs.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [cs.layout.create.element('input', {
				    		attr: {
				    			type: 'radio',
				    			name: 'host_uuid',
				    			value: d.uuid
				    		}
				    	})]
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col table_link',
				    	attr: {
				    		col: 'host_name',
				    		type: 'button',
				    		action: 'link',
				    		target: 'hosts?panel=details&host=' + d.uuid
				    	},
				    	text: d.name
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'host_uuid'
				    	},
				    	text: d.uuid
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'host_ip'
				    	},
				    	text: d.ip
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'host_distro'
				    	},
				    	text: d.sys.os.distro
				    }),
				    cs.layout.create.element('div', {
				    	css: 'table_col',
				    	attr: {
				    		col: 'host_type'
				    	},
				    	children: [cs.layout.create.element('img', {
				    		attr: {
				    			src: '/portal/static/images/os_' + d.type + '.png'
				    		}
				    	})]
				    })
				]
			}));
			
			// Refresh the page layout
			cs.layout.refresh();
		}
	});
	
	/**
	 * Method: Add Host Type
	 * 
	 * Toggle the host type in the add host form. Switch between the required fields
	 * depending on the host type, i.e. Windows or Linux.
	 * 
	 * @param {type} The host type to add, either 'linux' or 'windows'
	 */
	cs.register.method('host.add_type', function(type) {
		var l_fields = ['user', 'password'];
		var w_fields = ['dkey'];
		if (type != 'linux' && type != 'windows') {
			return false;
		}
		$('input[form="add_host"][name="type"]').val(type);
		cs.forms.all['add_host']['inputs']['type']['value'] = type;
		
		// Host type button
		function _host_type(s,t,l) {
			return cs.layout.create.element('div', {
				css:  'popup_row_toggle_button_50',
				attr: {
					state:  (s === true) ? 'active': 'inactive',
					type:   'button',
					target: 'host.add_type',
					arg:    t
				},
				text: l
			});
		}
		
		// Switch button states
		function _switch_buttons(a,i) {
			at = a.charAt(0).toUpperCase() + a.slice(1);
			it = i.charAt(0).toUpperCase() + i.slice(1);
			$('div[type="button"][arg="' + a + '"]').replaceWith(_host_type(true,a,at));
			$('div[type="button"][arg="' + i + '"]').replaceWith(_host_type(false,i,it));
		}
		
		// Enable the user/password fields
		if (type == 'linux') {
			$('div[class="popup_row"][host_type="windows"]').fadeOut('fast', function() {
				$('div[class="popup_row"][host_type="linux"]').fadeIn('fast');
			});
			$.each(l_fields, function(i,v) {
				cs.forms.all['add_host']['inputs'][v]['_disabled'] = false;
			});
			$.each(w_fields, function(i,v) {
				cs.forms.all['add_host']['inputs'][v]['_disabled'] = true;
			});
			_switch_buttons('linux', 'windows');
		}
		
		// Disable the user/password fields
		if (type == 'windows') {
			$('div[class="popup_row"][host_type="linux"]').fadeOut('fast', function() {
				$('div[class="popup_row"][host_type="windows"]').fadeIn('fast');
			});
			$.each(w_fields, function(i,v) {
				cs.forms.all['add_host']['inputs'][v]['_disabled'] = false;
			});
			$.each(l_fields, function(i,v) {
				cs.forms.all['add_host']['inputs'][v]['_disabled'] = true;
			});
			_switch_buttons('windows', 'linux');
		}
		return;
	});
});