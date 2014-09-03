/**
 * CloudScape Host Details
 */
cs.import('CSHostDetails', function() {
	
	/**
	 * Initialize CSHostDetails
	 * @constructor
	 */
	this.__init__ = function() {

		// Bind actions
		cs.hosts.bind();
		
		// Document ready
		$(document).ready(function() {
			//cs.hosts.init_timer();
			cs.hosts.layout();
		});
		
		// Window resize
		$(window).resize(function() {
			cs.hosts.layout();
		});
	}
	
	/**
	 * Bind Actions
	 */
	this.bind = function() {
		
		// Change host ownership
		$('select[name="owner"]').on('change', function() {
			var o = this.value;
			cs.layout.loading(true, 'Changing host ownership...', function() { 
				cs.api.request.post({
					path:   'host',
					action: 'update',
					_data:  {
						uuid:  cs.hosts.active(),
						owner: o
					}
				});
			});
		});
	}
	
	/**
	 * Get Active Host
	 * 
	 * Return the UUID of the active host from the URL.
	 */
	this.active = function() {
		return cs.url.param_get('host');
	}
	
	/**
	 * Set Layout
	 */
	this.layout = function() {
		$.each(['services', 'disk', 'memory', 'cpu', 'network', 'firewall'], function(i,_t) {
			var t = _t + '_overview';
			
			// Height attributes
			var height = {
				table: 		  $('#sysinfo_table').height(),
				title:		  $('#sysinfo_title').actual('outerHeight', {includeMargin: true}),
				tmpl:  		  $('.table_panel_tmpl').height(),
				panel_title:  $('div[class="table_panel_title"][table="' + t + '"]').actual('outerHeight', {includeMargin: true}),
				header_title: $('div[class="table_headers"][table="' + t + '"]').actual('outerHeight', {includeMargin: true})
			}
			
			// Define the height of the table
			var table_height = (height.table - (height.title + height.tmpl + height.panel_title + height.header_title + 10));
			
			// Set the height of the table
			$('div[type="table"][name="' + t + '"]').height(table_height + 'px');
		});
	}
	
	/**
	 * Create Service Row
	 */
	this.service_row = function(s) {
		
		// Define the service state string
		var state = (function() {
			if (s.state.active === true) {
				return (s.state.active === s.state.target) ? 'RUNNING' : 'STOPPING';
			}
			if (s.state.active === false) {
				return (s.state.active === s.state.target) ? 'STOPPED': 'STARTING';
			}
		})();
		
		// Construct and return the service row element
		return cs.layout.create.element('div', {
			css:  'table_row',
			attr: {
				service: s.name,
				style:   'opacity:1.0;',
				type:    'row'
			},
			children: [
			    cs.layout.create.element('div', {
			    	css:  'table_col',
			    	attr: {
			    		col: 'service_name'
			    	},
			    	text: s.name
			    }),
			    cs.layout.create.element('div', {
			    	css:  'table_col',
			    	attr: {
			    		col:   'service_state',
			    		state: state.toLowerCase()
			    	},
			    	text: state
			    }),
			    cs.layout.create.element('div', {
			    	css:  'table_col',
			    	attr: {
			    		col: 'service_state_control'
			    	},
			    	html: (function() {
			    		if (state == 'RUNNING' || state == 'STOPPED') {
			    			return cs.layout.create.element('div', {
			    				css:  'service_control_link',
			    				attr: {
			    					type:   'button',
			    					action: 'method',
			    					target: 'host.' + ((s.state.active === true) ? 'stop': 'start') + '_service',
			    					arg:    s.name
			    				},
			    				text: ((s.state.active === true) ? 'Stop' : 'Start') + ' service'
			    			});
			    		}
			    	})()
			    }),
			    cs.layout.create.element('div', {
			    	css:  'table_col',
			    	attr: {
			    		col:   'service_monitor',
			    		state: (s.monitor === true) ? 'enabled': 'disabled'
			    	},
			    	text: (s.monitor === true) ? 'ENABLED': 'DISABLED'
			    }),
			    cs.layout.create.element('div', {
			    	css:  'table_col',
			    	attr: {
			    		col: 'service_monitor_control'
			    	},
			    	html: cs.layout.create.element('div', {
			    		css:  'service_control_link',
			    		attr: {
			    			type:   'button',
			    			action: 'method',
			    			target: 'host.' + ((s.monitor === true) ? 'disable' : 'enable') + '_monitor',
			    			arg:    s.name
			    		},
			    		text: ((s.monitor === true) ? 'Disable' : 'Enable') + ' monitor'
			    	})
			    })
			]
		});
	}
	
	/**
	 * Callback: Remove Host Formula
	 * 
	 * Remove the host formula row from the DOM after making an API call to
	 * delete.
	 * 
	 * @param {d} The response data from the API server
	 */
	cs.register.callback('host.remove_formula', function(c,m,d,a) {
		$('div[uuid="' + d.uuid + '"][formula="' + d.formula + '"]').remove();
	});
	
	/**
	 * Callback: Set Service
	 */
	cs.register.callback('host.set_service', function(c,m,d,a) {
		
		// Update the service row
		$('div[service="' + d.service.name + '"]').replaceWith(cs.hosts.service_row(d.service));
		
		// Refresh the columns
		cs.layout.set.cols();
	});
	
	/**
	 * Method: Start Service
	 */
	cs.register.method('host.start_service', function(s) {
		cs.api.request.post({
			path:   'host/service',
			action: 'set',
			_data:  {
				uuid:    cs.hosts.active(),
				service: s,
				state:   true
			},
			callback: {
				id: 'host.set_service'
			}
		});
	});
	
	/**
	 * Method: Stop Service
	 */
	cs.register.method('host.stop_service', function(s) {
		cs.api.request.post({
			path:   'host/service',
			action: 'set',
			_data:  {
				uuid:    cs.hosts.active(),
				service: s,
				state:   false
			},
			callback: {
				id: 'host.set_service'
			}
		});
	});
	
	/**
	 * Method: Disable Monitor
	 */
	cs.register.method('host.disable_monitor', function(s) {
		cs.api.request.post({
			path:   'host/service',
			action: 'set',
			_data:  {
				uuid:    cs.hosts.active(),
				service: s,
				monitor: false
			},
			callback: {
				id: 'host.set_service'
			}
		});
	});
	
	/**
	 * Method: Enable Monitor
	 */
	cs.register.method('host.enable_monitor', function(s) {
		cs.api.request.post({
			path:   'host/service',
			action: 'set',
			_data:  {
				uuid:    cs.hosts.active(),
				service: s,
				monitor: true
			},
			callback: {
				id: 'host.set_service'
			}
		});
	});
	
	/**
	 * Method: Remove Host Formula
	 */
	cs.register.method('host.remove_formula', function() {
		cs.layout.popup_toggle(false, false, false, function() { 
			
			// Get the selected formula and active host
			var f = $('input[type$="radio"][name$="formula"]:checked').val();
			var h = cs.hosts.active();
			
			// Check if the user is uninstalling
			var u = (function() {
				var v = $('input[type="checkbox"][name="uninstall"]').val();
				return (v.contains(':true')) ? true : false;
			})();
			
			// Submit the API request
			cs.api.request.post({
				path:   'host/formula',
				action: 'remove',
				_data:  {
					uuid:      h,
					formula:   f,
					uninstall: u
				},
				callback: {
					id: 'host.remove_formula'
				}
			});
		});
	});
	
	/**
	 * Callback: Render Host Services
	 */
	cs.register.callback('host.render_services', function(c,m,d,a) {
		
		// Construct the host service rows
		$('div[type="table"][name="services_overview"]').html(cs.layout.create.element('div', {
			children: (function() {
				var services = {
					running: [],
					stopped: []
				};
				
				// Process each returned service
				$.each(m, function(i,s) {
					
					// Define the service state string
					var state = (function() {
						if (s.state.active === true) {
							return (s.state.active === s.state.target) ? 'RUNNING' : 'STOPPING';
						}
						if (s.state.active === false) {
							return (s.state.active === s.state.target) ? 'STOPPED': 'STARTING';
						}
					})();
					
					// Construct the service row element
					services[(function() {
						return (state == 'RUNNING' || state == 'STOPPING' || state == 'STARTING') ? 'running': 'stopped';
					})()].push({name: s.name, html: cs.hosts.service_row(s)});
				});
				
				// Sort worker
				function sort_worker(a,b) {
					if (a.name < b.name) { return -1; }
					if (a.name > b.name) { return 1;  }
					return 0;
				}
				
				// Sort running/stopped by name
				services.running.sort(sort_worker);
				services.stopped.sort(sort_worker);
				
				// Return the constructed service rows
				return (function() {
					var running = services.running.map(function(i) { return i.html });
					var stopped = services.stopped.map(function(i) { return i.html })
					return running.concat(stopped);
				})();
			})()
		}));
		
		// Refresh the columns
		cs.layout.set.cols();
	});
	
	/**
	 * Callback: Host Details Response Handler
	 * 
	 * Handle the response from the Socket.IO API proxy server when retrieving
	 * host stats, and render the appropriate line chart on the host details page.
	 * 
	 * @see cs.method['line_chart']();
	 * @see cs.method['stats_table']();
	 * @see cs.method['host_stats']();
	 * 
	 * @param {t} The target div for the chart or table, i.e. '#{t}'
	 * @param {d} The data for the chart or table
	 */
	cs.register.callback('host.render_stats', function(c,m,d,a) {
		
		// Line Charts
		$.each(m.chart, function(index,obj) {
			try {
				
				// Set the Y-axis and scale properties depending on the type
				y_axis = (obj.type == 'use') ? {}:{'buffer': 0.25};
				scale  = (obj.type == 'use') ? {}:{
					10240: {
						'convert': 'kb',
						'unit':    'KB/s'
					},
					10485760: {
						'convert': 'mb',
						'unit':    'MB/s'
					}
				};
				
				// Render the line chart
				cs.method['d3.line_chart'](index, obj, { 
					'height': 150,
					'y_axis': y_axis,
					'scale':  scale
				});
			// Failed to render line chart, die silently
			} catch (e) {}
		});
		
		// Data Tables
		$.each(m.table, function(index,obj) {
			try {
				cs.method['d3.stats_table'](index, obj);
			
			// Failed to render table data, die silently
			} catch (e) {}
		});
	});
	
	/**
	 * Get Services
	 * 
	 * Continually refresh host services.
	 */
	this.get_services = function() {
		cs.api.request.get({
			path:     'host/service',
			action:   'get',
			callback: {
				id: 'host.render_services'
			},
			_data:    {
				uuid: cs.hosts.active()
			}
		});
	}
	
	/**
	 * Initialize Timers
	 */
	this.init_timer = function() {
			
		// Initial method calls
		cs.hosts.get_services();
		cs.hosts.get_stats();
		
		// Recurring method calls
		//window.setInterval(function() {
		//	cs.hosts.get_services();
		//	cs.hosts.get_stats();
		//}, 10000);
	}
	
	/**
	 * Get Stats
	 * 
	 * Continually refresh host stats with a delay in seconds.
	 * 
	 * @see cs.method['host_stats]();
	 */
	this.get_stats = function() {
		cs.api.request.get({
			path:     'host',
			action:   'stats',
			callback: {
				id: 'host.render_stats'
			},
			_data:    {
				uuid: cs.hosts.active()
			}
		});
	}
	
	/**
	 * Update Table Summary
	 * 
	 * @param {t} The target host statistics table
	 * @param {n} The name of the summary row to update
	 * @param {v} The new value to set
	 */
	this.sum_update = function(t,n,v) {
		if ($('div[type="summary"][table="' + t + '"][name="' + n + '"]').length > 0) {
			$('div[type="summary"][table="' + t + '"][name="' + n + '"]').html(v);
		}
	}
});