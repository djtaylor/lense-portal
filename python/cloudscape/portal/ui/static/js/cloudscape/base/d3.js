cs.import('CSBaseD3', function() {
	
	/**
	 * Method: Render Stats Table
	 * 
	 * Render a host statistics table.
	 * 
	 * @param {t} The target div for the table, i.e. '#{t}'
	 * @param {d} The table data
	 */
	cs.register.method('d3.stats_table', function(t,d) {
		if ($('div[type$="table"][name$="' + t + '"]').length > 0) {
			div_rows = '';
			div_headers = null;
			$.each(d.data, function(i,o) {
				if (!defined(div_headers)) {
					h_inner = '<div class="table_header table_header_rg" col="' + d.key + '">' + d.labels[d.key] + '</div>';
					$.each(d.order, function(i,k) {
						if (k != d.key) {
							h_inner += '<div class="table_header table_header_rg" col="' + k + '">' + d.labels[k] + '</div>';
						}
					});
					div_headers = '<div class="table_headers">' + h_inner + '</div>';
				}
				r_inner = '';
				$.each(d.order, function(i,k) {
					r_inner += '<div class="table_col" col="' + k + '">' + o[k] + '</div>';
				});
				div_rows += '<div class="table_row">' + r_inner + '</div>';
			});
			div = '<div class="table_stats" type="table" name="' + t + '">' + div_headers + div_rows + '</div>';
			$('div[type$="table"][name$="' + t + '"]').replaceWith(div);
			
			// Refresh the page layout
			cs.layout.refresh();
		}
	});

	/**
	 * Method: Render Line Chart
	 * 
	 * Render a line chart, typically used to create a D3JS line chart for
	 * display host statistics. Will redraw the target SVG each time the method
	 * is called.
	 * 
	 * @param {t} The target div for the chart, i.e. '#{t}'
	 * @param {d} The data for the chart
	 * @param {h} The optional height in pixels of the chart
	 */
	cs.register.method('d3.line_chart', function(t,d,p) {
		
		// Create a date object and get the date range in a data set
		function _get_date(d) { return new Date(d); }
		function _get_date_range(_data_) {
			_all_dates = [];
			$.each(_data_.group, function(dk,dg) {
				$.each(dg.stats, function(i,k) {
					_all_dates.push(k.date);
				});
				return false;
			});
			return {
				'min': _get_date(_all_dates[0]),
				'max': _get_date(_all_dates[_all_dates.length-1])
			}
		}
		
		
		/**
		 * Extract Largest Data Value
		 * 
		 * Extract the largest data value from a dataset in each group.
		 * 
		 * @param {_data_} The data to extract from
		 */
		function _get_max_value(_data_) {
			_max_value = 0;
			$.each(_data_.group, function(dk,dg) {
				$.each(dg.stats, function(i,k) {
					$.each(k.data, function(p,r) {
						if (parseFloat(r) > parseFloat(_max_value)) {
							_max_value = r;
						}
					});
				});
			});
			return _max_value;
		}
		
		/**
		 * Convert Data
		 * 
		 * @param {_c} Conversion parameter
		 * @param {_v} Value to convert
		 */
		function _convert(_c,_v) {
			switch (_c) {
				case 'kb':
					return (_v / 1024);
				case 'mb':
					return ((_v / 1024) / 1024);
				case 'gb':
					return (((_v / 1024) / 1024) / 1024);
				default:
					return v;
			}
		}
		
		/**
		 * Scale Data
		 * 
		 * @param {_d} Data set to scale
		 * @param {c}  Conversion parameter
		 */
		function _scale_data(_d, c) {
			
			// Process each statistic group
			$.each(_d.group[0].stats, function(i,o) {
				_td = {}
				$.each(o.data, function(k,v) {
					_td[k] = _convert(c,v);
				});
				_d.group[0].stats[i].data = _td;
			});
			return _d;
		}
		
		/**
		 * Draw Group Chart
		 * 
		 * Handle each group of data in the submitted object and render a chart
		 * for each group.
		 * 
		 * @param {e}  The container div element
		 * @param {tw} The width of the container element
		 * @param {th} The height of the container element
		 * @param {d}  The group chart data
		 */
		function _draw_group_chart(e,tw,th,d,p) {
			
			// Get the minimum and maximum dates and values
			date_range = _get_date_range(d);
			max_value  = _get_max_value(d);
			
			// Handle variations in scale
			_unit = d.unit;
			if (defined(p.scale)) {
				$.each(p.scale, function(st, sp) {
					if (max_value > st) {
						max_value = _convert(p.scale[st].convert, max_value);
						d         = _scale_data(d, p.scale[st].convert);
						_unit     = sp.unit;
					}
				});
			}
			
			// Default parameters
			y_buffer   = (!defined(p.y_axis.buffer)) ? 0: (max_value * p.y_axis.buffer);
			
			// Set the X and Y scales
			var xS = d3.time.scale().domain([date_range.min, date_range.max]).range([0, tw]);
			var yS = d3.scale.linear().domain([0, (max_value + y_buffer)]).range([th, 0]);
			
			// Make the X and Y axis
			var xA = d3.svg.axis().scale(xS).orient('bottom');
			var yA = d3.svg.axis().scale(yS).orient('left');
			
			// Define the SVG
			var svg = d3.select('#' + t).append('svg').attr('id', 'svg_' + t)
				.attr('width', tw + 20).attr('height', th + 60)
			.append('g')
				.attr('transform', 'translate(' + 50 + ',' + 20 + ')');
			
			// Draw the X axis
			svg.append("g")
		    	.attr("class", "chart_x_axis")
		    	.attr("transform", "translate(0," + th + ")")
		    	.call(xA)
		    	
		    // Append the chart summary
		    .append('text')
		    	.attr('y', -(th + 10))
		    	.attr('x', (tw - 40))
		        .attr('text-anchor', 'end')
		    	.text(d.group[0].label + ': ' + d.label + ' (' + _unit + ')');
		    	
			// Functions to return chart grid lines
			function make_x_axis() {        
			    return d3.svg.axis().scale(xS).orient("bottom").ticks(50);
			}
			function make_y_axis() {        
			    return d3.svg.axis().scale(yS).orient("left").ticks(10);
			}
			
			// Draw the Y axis
			svg.append('g')
		     	.attr('class', 'chart_y_axis')
		     	.call(yA);
			
			// Construct the grid
			svg.append('g')         
	        	.attr('class', 'chart_grid')
	        	.attr('transform', 'translate(0,' + th + ')')
	        	.call(make_x_axis()
	        		.tickSize(-th, 0, 0)
	        		.tickFormat('')
	        	)
	        svg.append('g')         
	        	.attr('class', 'chart_grid')
	        	.call(make_y_axis()
	        		.tickSize(-tw, 0, 0)
	        		.tickFormat('')
	        	)
			
			// Draw each line
			$.each(d.group, function(gk,go) {
				
				// Set the color scale for this group
				var c  = d3.scale.category10();
				
				// Construct the data for each statistic group
				data_x = [];
				data_y = [];
				y_obj  = {};
				$.each(go.stats, function(sk,so) {
					data_x.push(so.date);
					$.each(d.data_keys.y, function(di,dk) {
						if (! y_obj.hasOwnProperty(dk)) {
							y_obj[dk] = []
						}
						y_obj[dk].push(so.data[dk])
					});
				});
				$.each(d.data_keys.y, function(di,dk) {
					data_y.push(y_obj[dk]);
				});
				
				// Define the graph line
				var line = d3.svg.line().x(function(d,i) {return xS(_get_date(data_x[i])); }).y(yS);
				
				// If rendering a usage graph
				if (d.type == 'use') {
					ac = data_y.length;
					ai = 0;
					var area = d3.svg.area().x(function(d,i) {return xS(_get_date(data_x[i])); }).y0(th).y1(yS);
					while ((ai + 1) <= ac) {
						use_y = [data_y[ai]]
						if (d.data_keys.y[ai] == 'used') {
							svg.selectAll('.line')
								.data(use_y)
								.enter()
							.append('path')
								.attr('class', 'table_area_used')
								.attr('d', area);
						}
						svg.selectAll('.line')
							.data(use_y)
							.enter()
						.append('path')
							.style('stroke', function(d) { return c(d); })
							.style('fill', 'none').style('stroke-width', '2px').attr('d', line);
						ai++;
					}
					
					// Update the table summary
					var sum = {'total': null, 'free': null, 'used': null};
					data_y.forEach(function(o,i) {
						if (d.data_keys.y[i] == 'used') {
							sum.used  = o[o.length-1];
						} else {
							sum.total = o[o.length-1];
						}
					});
					sum.free = sum.total - sum.used;
					$.each(sum, function(k,v) {
						if (cs.hasOwnProperty('hosts')) {
							console.log(go.label);
							console.log(k);
							console.log(v);
							cs.hosts.sum_update(go.label, k, v);
						}
					});
					
				} else {
					svg.selectAll('.line')
						.data(data_y)
						.enter()
					.append('path')
						.style('stroke', function(d) { return c(d); })
						.style('fill', 'none').style('stroke-width', '2px').attr('d', line);
				}
			});
		}
		
		// Make sure the target chart div is rendered
		if ($('div[type$="svg"][name$="' + t +'"]').length > 0) {
			var e = $('div[type$="svg"][name$="' + t +'"]');
			
			// Delete the old SVG contents
			$.each(e.find('svg'), function(i,o) { $(o).remove(); });
			
			// Make sure data is available
			var data_available = false;
			$.each(d.group, function(i,_g) {
				if (!$.isEmptyObject(_g.stats)) {
					data_available = true;
				}
			});
			
			// If no data is available
			if (!data_available) {
				e.append(cs.layout.create.element('div', {
					css: 'table_chart_nodata',
					text: 'No data available'
				}));
				return;
			}
			
			// Set the chart width and height
			var tw = $('.table_panel_tmpl').width() - 40;
			var th = !defined(p.height) ? $(e).height() - 40 : p.height - 40;
			
			// Handle multiple groups
			$.each(d['group'], function(i,o) {
				_ld = d
				_ld['group'] = [o]
				_draw_group_chart(e,tw,th,_ld,p);
			});
		}
	});
});