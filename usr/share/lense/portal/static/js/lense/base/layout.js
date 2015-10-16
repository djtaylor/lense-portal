/**
 * Lense Base Layout Class
 * 
 * Class to handle page layout and element positioning.
 */
lense.import('LenseBaseLayout', function() {
	
	// Alert counter
	var alert_count = 1;
	
	/**
	 * Render Alert Box
	 * 
	 * This method is used to render alert messages to the dashboard with different styles depending
	 * on the message type argument.
	 * 
	 * @param {type} The type of message to render
	 * @param {msg}  The message text to display
	 */
	this.render = function(type, msg) {
		var container = '#alert_box_container';
		
		// Close alert box
		var close_alert = lense.layout.create.element('div', {
			css:  'alert_close',
			attr: {
				alert: alert_count
			},
			text: 'Close'
		});
		
		// Define the alert title
		var alert_title = type.charAt(0).toUpperCase() + type.slice(1);
		
		// Does the message have a type?
		var no_type = false;
		
		// Process based on message type
		switch(type) {
			case 'fatal':
			case 'error':
			case 'warn':
				$(container).prepend(lense.layout.create.element('div', {
					css:  'alert_box',
					id:   'alert_' + alert_count,
					children: [
				        close_alert,
				        lense.layout.create.element('div', {
				        	css: 'alert_box_msg',
				        	children: [
				        	    lense.layout.create.element('div', {
				        	    	css: 'alert_box_' + type,
				        	    	text: alert_title + ':'
				        	    })
				        	],
				        	text: msg
				        })
					]
				}));
				break;
			case 'success':
			case 'info':
				var alert_title = type.charAt(0).toUpperCase() + type.slice(1);
				$("#alert_box_container").prepend("<div class='alert_box' id='alert_" + alert_count + "'><div class='alert_box_msg'><div class='alert_box_" + type + "'>" + alert_title + ":</div>" + msg + "</div></div>");
				break;
			default:
				var no_type = true;
				$("#alert_box_container").prepend("<div class='alert_box' id='alert_" + alert_count + "'>" + close_alert + type + ": " + msg + "</div>");
				break;
		}
		if (type == 'fatal' || type == 'error' || type == 'warn') {
			$('.alert_close').click(function(e) {
				box_num = e.target.attributes.alert.value;
				$('#alert_' + box_num).fadeOut('fast', function() {
					this.remove();
				});
			});
		}
		if (type == 'success' || type == 'info' || no_type === true) {
			$('#alert_' + alert_count).delay(3000).fadeOut('fast', function() {
				this.remove();
			});
		}
		alert_count++;
	}
	
	/**
	 * Fade Out Element
	 * 
	 * Wrapper method to fade out an element because. No real point in this method,
	 * but since I have 'fadein' might as well have 'fadeout'.
	 * 
	 * @param {f} A jQuery selector
	 * @param {c} A callback function
	 */
	this.fadeout = function(f,c) {
		$(f).fadeOut('fast', function() {
			if (defined(c)) {
				c();
			}
		});
	}
	
	/**
	 * Fade In Element
	 * 
	 * Wrapper method to fade in an element that is either set to hidden or opacity
	 * is set to 0.
	 * 
	 * @param {f} A jQuery selector
	 * @param {c} A callback function
	 */
	this.fadein = function(f,c) {
		if ($(f).css('display') == 'none') {
			$(f).fadeIn('fast');
		}
		if ($(f).css('opacity') == 0) {
			$(f).animate({
				opacity: 1.0
			}, 100);
		}
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Remove Element
	 * 
	 * Fade out then completely remove an element from the DOM.
	 * 
	 * @param {f} A jQuery selector
	 */
	this.remove = function(f) {
		$(f).fadeOut('fast', function() {
			this.remove();
		});
	}
	
	/**
	 * Get HTML
	 * 
	 * Helper method to flatten either a single or array of jQuery nodes into a single
	 * HTML string.
	 * 
	 * @param {e} Either a single jQuery node or an array of nodes
	 */
	this.html = function(e) {
		if (e instanceof jQuery) {
			return e[0].outerHTML;
		} else {
			ha = [];
			$.each(e, function(i,o) {
				ha.push(o[0].outerHTML);
			});
			return ha.join('');
		}
	}
	
	/**
	 * Layout Completed
	 */
	this.complete = function() {
		var t = ['.table_headers', '.table_row'];
		$.each(t, function(i,k) {
			$.each($(document).find(k), function(i,o) {
				$(this).delay(20*i).animate({
					opacity: 1.0
				}, 100);
			});
		});
	}
	
	/**
	 * Create Layout Element
	 */
	this.create = {
		
		/**
		 * Create Table Elements
		 * 
		 * Helper method used to generate different predefined table elements.
		 */
		table: {
			
			/**
			 * Create Table Action Buttons
			 */
			action: function(p) {
				return lense.layout.create.element('div', {
					css:  'table_action',
					attr: (function() {
						var b = { type: 'button' };
						$.each(p.attr, function(k,v) {
							b[k] = v;
						});
						return b;
					})(),
					text: p.text
				});
			},
			
			/**
			 * Create Table Headers
			 */
			headers: function(p) {
				var size = (p.hasOwnProperty('size')) ? p.size : 'md';
				var mw   = (p.hasOwnProperty('minwidth')) ? p.minwidth : '150';
				return lense.layout.create.element('div', {
					css: 'table_headers',
					children: (function() {
						var c = [];
						
						// Select header column
						if (p.hasOwnProperty('select') && p.select !== false) {
							c.push(lense.layout.create.element('div', {
								css: 'table_select_header'
							}));
						}
						
						// Scan the column keys
						$.each(p.keys, function(k,l) {
							c.push(lense.layout.create.element('div', {
								css:  'table_header table_header_md',
								attr: {
									col: k,
									mw:  mw
								},
								text: l
							}));
						});
						
						// Return the header columns
						return c;
					})()
				});
			},
			
			/**
			 * Create Table Row
			 */
			row: function(p) {
				
			},
			
			/**
			 * Create Table Panel
			 * 
			 * Create a table parent panel for child table elements.
			 *
			 * @param {p} The table panel parameters
			 */
			panel: function(p) {
				
				// Construct the title element
				pt = lense.layout.create.element('div', {
					css:  'table_panel_title table_panel_link',
					attr: {
						type:   'button',
						action: 'toggle',
						target: p.name
					},
					text: p.title
				});
				
				// Construct any table actions
				pa = null;
				if (p.hasOwnProperty('actions') && !$.isEmptyObject(p.actions)) {
					pa = lense.layout.create.element('div', {
						css:  'table_actions_inner',
						attr: (p.actions.hasOwnProperty('attr')) ? p.actions.attr : {},
						children: p.actions.objects
					});
				}
				
				// Construct table panel
				pm = lense.layout.create.element('div', {
					css:  'table_window',
					attr: {
						type: 'toggle',
						name: p.name
					},
					children: [lense.layout.create.element('div', {
						css:  'table_rows',
						attr: {
							type:   'rows',
							target: p.name
						},
						html: (function() {
							var t = (defined(pa)) ? pa : '';
							t += p.rows.join('');
							return t;
						})()
					})]
				});
				
				// Return the table panel
				return (pt + pm);
			}
		},
			
		/**
		 * Create Popup Elements
		 * 
		 * Helper method used to generate different predefined popup elements.
		 */
		popup: {
			
			/**
			 * Create Popup Container
			 * 
			 * Create a popup parent container for child popup elements.
			 * 
			 * @param {p} Popup container parameters
			 */
			container: function(p) {
				return lense.layout.create.element('div', {
					css:  'popup_content',
					attr: {
						type:   'popup',
						target: p.target
					},
					children: p.children
				});
			},
			
			/**
			 * Create Popup Title Element
			 * 
			 * Create a popup title used at the top of a popup content window.
			 * 
			 * @param {t} The text attribute
			 */
			title: function(t) {
				return lense.layout.create.element('div', {
					css:  'popup_title',
					text: t
				})
			},
			
			/**
			 * Create Popup Header Element
			 * 
			 * Create a popup header used to seperate groups of elements. This is different
			 * from a popup title.
			 * 
			 * @param {t} The text attribute
			 */
			header: function(t) {
				return lense.layout.create.element('div', {
					css:  'popup_row_header',
					text: t
				})
			},
			
			/**
			 * Create Popup Row Element
			 * 
			 * Create a popup row element with a set of parameters.
			 * 
			 * @param {p} Popup row parameters
			 */
			row: function(p) {
				
				
				// Label/inner HTML combination
				if (p.hasOwnProperty('label') && p.hasOwnProperty('inner')) {
					return lense.layout.create.element('div', {
						css: 'popup_row',
						children: [
						    lense.layout.create.element('div', {
						    	css:  'popup_row_label',
						    	html: p.label
						    }),
						    lense.layout.create.element('div', {
				    			css: 'popup_row_text_outer',
				    			children: p.inner
				    		})
						]
					});
				}
				
				// Label/text combination
				if (p.hasOwnProperty('label') && p.hasOwnProperty('text')) {
					return lense.layout.create.element('div', {
						css: 'popup_row',
						children: [
						    lense.layout.create.element('div', {
						    	css:  'popup_row_label',
						    	html: p.label
						    }),
						    lense.layout.create.element('div', {
						    	css:  'popup_row_text',
						    	html: p.text
						    })
						]
					});
				}
			}
		},
			
		/**
		 * Create Element
		 *
		 * Create a new HTML element using supplied parameters.
		 * 
		 * @param {t} The type of element
		 * @param {p} The element properties
		 */
		element: function(t,p) {
			var elem = function() {
				var double = ['div', 'option', 'select', 'p'];
				return (double.contains(t)) ? $('<' + t + '></' + t + '>') : $('<' + t + '/>');
			}();
		
			// Class
			if (p.hasOwnProperty('css')) {
				elem.addClass(p.css);
			}
			
			// Attributes
			if (p.hasOwnProperty('attr')) {
				elem.attr(p.attr);
			}
		
			// HTML
			if (p.hasOwnProperty('html')) {
				elem.html(p.html);
			}
			
			// Text
			if (p.hasOwnProperty('text')) {
				elem.text(p.text);
			}
			
			// ID
			if (p.hasOwnProperty('id')) {
				elem.attr('id', p.id);
			}
			
			// Children
			if (p.hasOwnProperty('children')) {
				$.each(p.children, function(i,v) {
					elem.append(v);
				});
			}
			
			// Return the constructed HTML
			return lense.layout.html(elem);
		}
	}
	
	/**
	 * Response Content
	 * 
	 * Toggle the response div. Typically used when validating form submissions.
	 * 
	 * @param {s} Boolean value, show or hide the popupe response
	 * @param {p} An object of parameters
	 * @param {c} Optional callback with no parameters
	 */
	this.show_response = function(s,p,c) {
		if (s === true) {
			$('div[type$="response"][target$="' + p['tgt'] + '"]').replaceWith('<div class="form_response" type="response" target="' + p['tgt'] + '">' + p['msg'] + '</div>');
		} else {
			$('div[type$="response"][target$="' + p['tgt'] + '"]').replaceWith('<div class="form_response" style="display:none;" type="response" target="' + p['tgt'] + '"></div>');
		}
		
		// Run the callback
		if (c) { c(); }
	}
	
	/**
	 * Toggle Popups
	 * 
	 * Helper method to either fade in or fade out popups. Accepts the target popup content
	 * window to fade in addition to the popups container, as well as a callback function.
	 * 
	 * @param {s} Boolean value, show or hide the popupe
	 * @param {t} The target popup attribute string to show
	 * @param {p} Override the parent popup window class
	 * @param {c} Optional callback with no parameters
	 */
	this.popup_toggle = function(s,t,p,c) {
		var top  = $(window).scrollTop();
		var left = $(window).scrollLeft();
		p = (!defined(p)) ? '.popups' : '.' + p;
		
		// Get the popup element
		var e = $('div[type="popup"][target="' + t + '"]');
		
		// Fade in popup
		if (s === true) {
			
			// Content specific title/body height
			var ct = e.find('.popup_title').actual('outerHeight', {includeMargin:true});
			var cb = e.find('.popup_body').actual('height');
			
			// Autoset the popup content height
			e.height((ct + cb) + 'px');
			
			// Show the popup element
			$(p).fadeIn('fast', function() {
				e.fadeIn('fast', function() {
					$('html, body').css({
						overflow: 'hidden',
						height:   '100%'
					});
				});
			});
			
		// Fade out popup
		} else {
			$('div[type="popup"]').fadeOut('fast', function() {
				$(p).fadeOut('fast', function() {
					$('html, body').css({
						overflow: 'auto',
						height:   'auto'
					});
				});
			});
		}
		
		// Run the callback
		if (c) { c(); }
	}
	
	/**
	 * Loading Window
	 * 
	 * Method to trigger the loading window. This method can be used to enable and disable
	 * the loading window, as well as set the text content.
	 * 
	 * @param {s} Boolean value, show or hide the loading window
	 * @param {m} Optional loading message
	 * @param {c} Callback function with no parameters
	 */
	this.loading = function(s,m,c) {
		if (s === true) {
			text = !defined(m) ? 'Loading, please wait...' : m;
			$('.loading_text').replaceWith('<div class="loading_text">' + text + '</div>');
			$('.loading').css('display', 'block');
		} else if (s === false) {
			$('.loading').css('display', 'none');
		} else if (s == 'update') {
			$('.loading_text').replaceWith('<div class="loading_text">' + m + '</div>');
		} else { return false; }
		
		// Run the callback
		if (c) { c(); }
	}
	
	/**
	 * Center Fixed Dimension/Position Element
	 * 
	 * Center an element on the page. The element must be fixed width and fixed position 
	 * for this to work correctly.
	 * 
	 * @param {elem} The element to center relative to the window
	 */
	this.center_elem = function(elem) {
		function _center(e) {
			var et = ($(window).height() / 2) - ($(e).height() / 2);
			var el = ($(window).width() / 2) - ($(e).width() / 2);
			$(e).css('top',et+'px');
			$(e).css('left',el+'px');
		}
		
		// Accept an array of elements or a single element
		if (elem instanceof Array) { elem.forEach(function(e) { _center(e); }); } 
		else { _center(e); }
	}
	
	/**
	 * Set Page Elements
	 */
	this.set = {
			
		/**
		 * Set Content Attributes
		 */
		content: function() {
			if ($('.base_window').length > 0) {
				var b_e = $('.base_window'),
				    b_t = b_e.css('padding-top').match(/(^[\d]*)px$/)[1],
				    b_b = b_e.css('padding-bottom').match(/(^[\d]*)px$/)[1],
				    b_p = (function() {
				    	var a = ($('.page_header_box').length > 0) ? $('.page_header_box').actual('outerHeight', { includeMargin: true }): 0;
				    	var b = ($('.table_title_ex').length > 0) ? $('.table_title_ex').actual('outerHeight', { includeMargin: true }): 0;
				    	return a + b;
				    })(),
				    b_h = (($(window).height()) - (parseInt(b_t) + parseInt(b_b))),
				    t_h = (($(window).height()) - (parseInt(b_t) + parseInt(b_b) + parseInt(b_p)));
				
				// Set the base and content window heights
				$('.base_window, .content_window').height(b_h);
				
				// Set the table heights
				$('.table, .table_50').height(t_h - 10);
				
				// Set any 50% tables that have an outer container
				$('.table_50_outer').each(function(i,o) {
					var width = ($(o).actual('width') / 2) - 5;
					$(o).find('.table_50').each(function(i,n) {
						$(n).css({
							width: (width) + 'px',
							margin: (i === 0) ? '0 5px 0 0':'0 0 0 5px',
							padding: '0'
						});
					});
				});
				
				// Dropdown popup action
				dpa_width = $('.dropdown_menu').actual('width') - $('div[type="icon"]').actual('outerWidth', {includeMargin: true});
				$('.dropdown_action').width(dpa_width);
				
				// Dropdown popup value
				dpv_width = dpa_width - $('.dropdown_button').actual('outerWidth', {includeMargin: true});
				$('.dropdown_value').width(dpv_width);
			}
		},
		
		/**
		 * Set Table Panels
		 */
		panels: function() {
			
			// Get all tables
			var t_a = $('div[class="table"][target]');
			
			// Set up every table that has an associated panel
			$.each(t_a, function(i,o) {
				
				// Get the target table
				var t_t = get_attr(o).target;
				
				// Look for an associated panel
				var t_p = $('div[class="table_panel"][target="' + t_t + '"]');
				
				// Reset the main table width
				$(o).css('width', '100%');
				
				// Set the table/panel dimensions
				var t_w = $(o).actual('outerWidth', { includeMargin: true }) - t_p.actual('outerWidth', { includeMargin: true });
				var t_h = $(o).actual('outerHeight', {includeMargin: true });
				
				// Update the table panel attributes
				t_p.css('height', t_h + 'px');
				
				// Update the table attributes
				$(o).css('width', t_w + 'px');
			});
		},
		
		/**
		 * Set Popup Attributes
		 */
		popups: function(t) {
			
			// Set the target element positioning
			$(t).css('position', 'absolute');
			
			// Get the popup dimensions
			h_c = $(t).actual('outerHeight');
			h_t = $('.popup_title').actual('outerHeight', {includeMargins:true});
			h_b = (h_c - h_t) - 45;
			
			// Set the dimensions of the popup body
			$('.popup_body').height(h_b + 'px');
			
			// Dropdown popup action
			dpa_width = $('.dropdown_menu').actual('width') - $('div[type="icon"]').actual('width');
			$('.dropdown_popup_action').width(dpa_width);
			
			// Dropdown popup value
			dpv_width = dpa_width - $('.dropdown_button').actual('width');
			$('.dropdown_value').width(dpv_width);
		},
			
		/**
		 * Set Menu Positions
		 */
		menus: function() {
			if ($($('.nav_dropdown_wrapper')).length > 0) {
				$.each($('.nav_dropdown_wrapper'), function(i,o) {
					attr   = get_attr(o);
					parent = $(attr.parent);
					offset = parent.offset();
					$(o).css('left', offset.left + 'px');
				});
			}
		},
			
		/**
		 * Set Column Dimensions
		 * 
		 * Method to look for table element groups on the page, and set the dimesions for
		 * the columns. This looks for the widest element in each column, and uses this
		 * value for the column width.
		 */
		cols: function() {
			var padding = 20;
			
			// Build an array of unique column elements
			columns = new Array();
			$('div[col]').each(function(index, elem) {
				column_id = this.attributes.col.value;
				if ($.inArray(column_id, columns) == -1) {
					columns.push(column_id)
				}
			});
			
			// Reset the columns
			$(columns).each(function(index, col) {
				$('div[col="' + col + '"]').css('width', 'auto');
			});
			
			// Set the width for each column ID
			$(columns).each(function(index, col) {
				var cw = 0;
				$('div[col="' + col + '"]').each(function(index, elem) {
					var ea = get_attr(elem);
					var aw = $(this).actual('width');
					var mw = (ea.hasOwnProperty('mw')) ? parseInt(ea.mw) : 0;
					cw = (aw > mw) ? ((aw > cw) ? aw : cw): ((mw > cw) ? mw : cw);
				});
				$('div[col="' + col + '"]').width((cw + (padding * 2)) + 'px');
			});
		}
	}
	
	/**
	 * Refresh Page Layout
	 * 
	 * Wrapper method used to refresh various elements on the page, after setting new
	 * content, updating tables, etc.
	 * 
	 * @param {p} Optional parameters that can be passed to the internal methods
	 */
	this.refresh = function(p) {
		
		// Set up the page
		$.each(lense.layout.set, function(f,o) {
			if (f !== 'popups') {
				lense.layout.set[f]();
			}
		});
		
		// Resizable elements
		$('div[resizable]').resizable({
			minHeight: 500,
			minWidth:  500,
			create: function(e,u) {
				lense.layout.set.popups(e.target);
			},
			resize: function(e,u) {
				lense.layout.set.popups(e.target);
			}
		});
		
		// If centering any elements
		if (defined(p) && p.hasOwnProperty('center')) {
			lense.layout.center_elem(p.center);
		}
		
		// Layout ready
		lense.layout.complete();
	}
});