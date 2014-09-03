cs.import('CSAdminDatacentersDetails', function() {
	
	/**
	 * Initialize CSAdminDatacentersDetails
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load datacenter statistics
		cs.admin.datacenters.stats();
		
		// Refresh every 10 seconds
		window.setInterval(function() {
			cs.admin.datacenters.stats();
		}, 10000);
		
		// Jump to another datacenter
		$('select[name="datacenter_jump"]').on('change', function() {
			if (cs.url.param_get('datacenter') != this.value) {
				window.location = '/portal/admin?panel=datacenters&datacenter=' + this.value;
			}
		});
	}
	
	/**
	 * Get Datacenter Statistics
	 */
	this.stats = function() {
		cs.api.request.get({
			path:     'cluster',
			action:   'stats',
			callback: {
				id: 'datacenter.stats'
			},
			_data: {
				filter: {
					datacenter: cs.url.param_get('datacenter')
				}
			}
		});
	}
	
	/**
	 * Callback: Render Datacenter Status
	 */
	cs.register.callback('datacenter.stats', function(c,m,d,a) {
		var sw = $('.table_panel_tmpl').width() - 10;
		var sh = 50;
		
		/**
		 * Render Summary Bar
		 * 
		 * @param {id} The ID of the bar chart to update
		 * @param {sd} Summary dictionary of name/index pairs
		 * @param {bd} The bar data to use
		 */
		function _render_sum_bar(id,sd,bd) {
			
			// Delete the old element
			$('#' + id).remove();
			
			// Update any summary rows
			$.each(sd, function(n,i) {
				$('div[type$="summary"][name$="' + n +'"]').text(bd[i]);
			});
			
			// Define the SVG
			var bar_svg = d3.select('div[type$="svg"][name$="' + id + '"]')
				.append('svg')
				.attr('id', id)
				.attr('width', sw)
				.attr('height', sh)
			.append('g')
				.attr('transform', 'translate(' + 10 + ',' + 10 + ')');
			
			// Get the sizes for each side of the visualization
			b_used = (parseFloat(bd.percent_used) * parseFloat(sw)) / 100.0;
			b_free = (parseFloat(bd.percent_free) * parseFloat(sw)) / 100.0;
			
			// Percent used
			var rect_used = bar_svg.append('rect')
				.attr('x', 0)
				.attr('y', 0)
				.attr('width', b_used)
				.attr('height', sh)
				.attr('fill', '#616161');
			
			// Percent free
			var rect_used = bar_svg.append('rect')
				.attr('x', b_used)
				.attr('y', 0)
				.attr('width', b_free)
				.attr('height', sh)
				.attr('fill', '#009FE3');
		}
		
		/**
		 * Render Line Chart
		 * 
		 * @param {id} The line chart ID
		 * @param {cd} The line chart data
		 * @param {k}  The line chart key
		 */
		function _render_line_chart(id,cd,k) {
			cs.method['d3.line_chart'](id, cd['chart'][k], { 
				'height': 150,
				'y_axis': {
					'buffer': 0.25
				},
				'scale': {
					10240: {
						'convert': 'kb',
						'unit':    'KB/s'
					},
					10485760: {
						'convert': 'mb',
						'unit':    'MB/s'
					}
				}
			});
		}
		
		// Line charts
		line_charts = {
			'disk_io': {
				'id': 'datacenter_diskio'
			},
			'net_io':  {
				'id': 'datacenter_netio'
			}
		}
		
		// Summary bar charts
		bar_charts = {
			'mem':  {
				'id':  'datacenter_mem',
				'sum': {
					'mem_mbtotal': 'mb_total',
					'mem_mbused':  'mb_used',
					'mem_mbfree':  'mb_free'
				}
			},
			'disk': {
				'id':  'datacenter_disk',
				'sum': {
					'disk_gbtotal': 'gb_total',
					'disk_gbused':  'gb_used',
					'disk_gbfree':  'gb_free'
				}
			},
			'cpu':  {
				'id':  'datacenter_cpu',
				'sum': {
					'cpu_cores':    'cores',
					'cpu_ghztotal': 'ghz_total',
					'cpu_ghzused':  'ghz_used',
					'cpu_ghzfree':  'ghz_free'
				}
			}
		}
		
		// Render the bar charts
		$.each(bar_charts, function(i,o) {
			_render_sum_bar(o.id, o.sum, m[i]);
		});
		
		// Render line charts
		$.each(line_charts, function(i,o) {
			_render_line_chart(o.id, m[i], i);
		});
	});
});