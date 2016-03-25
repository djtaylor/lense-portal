lense.import('Admin_HandlerDetails', function() {
	
	// Request map
	this.rmap   = null;
	
	// Handler name
	this.name   = null;
	
	// Handler window
	this.window = null;
	
	// Handler state
	this.edit_state = {
		locked: 'no',
		locked_by: undefined
	};
	
	/**
	 * Initialize LenseAdminHandlerDetails
	 * @constructor
	 */
	this.__init__ = function() {

		// Load handler details
		lense.admin.handler.load();

		// Bind button actions
		lense.admin.handler.bind();
		
		// Document ready
		$(document).ready(function() {
			lense.admin.handler.set_input();
			lense.admin.handler.set_dimensions();
			lense.admin.handler.set_window();
			lense.admin.handler.state();
			lense.admin.handler.check_page_state();
		});
		
		// Window resize
		$(window).resize(function() {
			lense.admin.handler.set_dimensions();
		});
	}
	
	/**
	 * Bind Button Actions
	 */
	this.bind = function() {
		
		// Jump to another handler
		$('select[name="handler_jump"]').on('change', function() {
			if (lense.admin.handler.active() != this.value) {
				window.location = '/admin?panel=handlers&handler=' + this.value;
			}
		});
	}
	
	/**
	 * Get Activate Handler
	 */
	this.active = function() {
		return $('input[type="hidden"][form="edit_handler"][name="uuid"]').val(); 
	}
	
	/**
	 * Load Handler Request Map
	 */
	this.load = function() {
		
		// Retrieve the handler request map and name
		lense.admin.handler.rmap = clone(handler_rmap);
		lense.admin.handler.name = handler_name;
		
		// Delete the containing element
		$('#handler_load').remove();
	}
	
	/**
	 * Lock Handler
	 * 
	 * @param {u} The username that has locked the handler.
	 * @param {c} Optional callback function
	 */
	this.lock = function(u,c) {
		lense.admin.handler.edit_state = { locked: 'yes', locked_by: u };
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Unlock Handler
	 * 
	 * @param {c} Optional callback function
	 */
	this.unlock = function(c) {
		lense.admin.handler.edit_state = { locked: 'no', locked_by: undefined };
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Change Detection
	 */
	this.changed = function() {
		$('input[name$="saved"]').val('no');
		$('input[name$="validated"]').val('no');
		
		// Change value in the menu info div
		$('.edit_menu_info').html('You must validate changes before saving');
		
		// Switch classes on the buttons
		lense.admin.handler.button_state('toggle', {
			act:  true, 
			tgt:  'handler.validate', 
			name: 'Validate'
		}, function() {
			lense.admin.handler.button_state('toggle', {
				act:  false, 
				tgt:  'handler.save', 
				name: 'Save'
			});
		});
	}
	
	/**
	 * Set Input Events
	 */
	this.set_input = function() {
		
		// <input> elements
		$('input[form="edit_handler"]').each(function(i,o) {
			$(o).on('change', function() {
				lense.admin.handler.changed();
			});
		});
		
		// <select> elements
		$('select[form="edit_handler"]').each(function(i,o) {
			$(o).on('change', function() {
				lense.admin.handler.changed();
			});
		});
	}
	
	/**
	 * Set Handler Dimensions
	 */
	this.set_dimensions = function() {
		edit_height   = ($(window).height() - $('.base_nav').height()) - 20;
		sidebar_width = $('.sidebar').width();
		edit_width    = ($(window).width() - 20);
		header_height = $('.page_header_box').height();
		menu_height   = $('.edit_menu').height();
		editor_height = edit_height - menu_height - header_height - 20;
		
		// Set the editor width and height
		$('.handler_edit').height(edit_height);
		$('.editor').height(editor_height);
		$('.handler_edit').width(edit_width);
		$('.editor').width(edit_width - sidebar_width - 10);
		$('.sidebar').height(editor_height - 20);
	}
	
	/**
	 * Set Handler Window
	 */
	this.set_window = function() {
		
		// Set the mode
		mode = 'ace/mode/json';
		
		// Create the editor instance
		lense.admin.handler.window = ace.edit('edit_0');
		lense.admin.handler.window.setTheme('ace/theme/chrome');
		lense.admin.handler.window.getSession().setMode(mode);
		lense.admin.handler.window.getSession().setUseWrapMode(true);
		
		// Set the editor contents
		lense.admin.handler.window.setValue(JSON.stringify(lense.admin.handler.rmap, null, '\t'), -1);
		
		// Detect if changes have been made and require validation
		lense.admin.handler.window.on('change', function(e) {
			lense.admin.handler.changed();
		});
	}
	
	/**
	 * Switch Button States
	 */
	this.button_state = function(t,p,cb) {
		if (t != 'switch' && t != 'toggle') { return false; }
		if (t == 'toggle') {
			c = p['act'] === true ? 'edit_menu_button_active' : 'edit_menu_button_inactive';
			s = p['act'] === true ? 'yes' : 'no';
			$('div[type$="button"][target$="' + p['tgt'] + '"]').replaceWith('<div class="' + c + '" type="button" action="method" target="' + p['tgt'] + '" active="' + s + '">' + p['name'] + '</div>');
		}
		if (t == 'switch') {
			$('div[type$="button"][target$="' + p['src'] + '"]').replaceWith('<div class="edit_menu_button_active" type="button" action="method" target="' + p['tgt'] + '" active="yes">' + p['name'] + '</div>');
		}
		if (cb) { cb(); }
	}
	
	/**
	 * Edit State
	 * 
	 * @param {s} The editing state
	 */
	this.state = function(s) {
		
		// Set Edit State
		if (defined(s) || s === false) {
			
			// Toggle readonly depending on the state
			lense.admin.handler.window.setReadOnly((s === true) ? false : true);
			
			// Set page elements
			if (s === true) {
				lense.admin.handler.lock(lense.api.client.params.user, function() {
					lense.url.param_set('edit', 'yes');
					$('.page_title').text(lense.admin.handler.name + ' - Edit Handler');
					
					// Enable form elements
					$('input[form="edit_handler"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
					$('select[form="edit_handler"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
				});
			} else {
				lense.admin.handler.unlock(function() {
					lense.url.param_set('edit', 'no');
					$('.page_title').text(lense.admin.handler.name + ' - View Handler');
					
					// Disable form elements
					$('input[form="edit_handler"]').each(function(i,o) {
						$(o).attr('disabled', '');
					});
					$('select[form="edit_handler"]').each(function(i,o) {
						$(o).attr('disabled', '');
					});
				});
			}
			
		// Check Edit State
		} else {
			
			// Look for the editing parameter
			edit_param = lense.url.param_get('edit');
			
			// If the editing parameter is not set
			if (!defined(edit_param)) {
				if (lense.admin.handler.edit_state.locked == 'yes') {
					if (lense.admin.handler.edit_state.locked_by == lense.api.client.params.user) {
						lense.method['handler.open']({'uuid': lense.admin.handler.active()});
					}
				} else { 
					lense.admin.handler.state(false); 
				}
			} else {
				if (edit_param == 'yes') {
					lense.method['handler.open']({'uuid': lense.admin.handler.active()});
				} else { 
					lense.admin.handler.state(false); 
				}
			}
		}
	}
	
	// Monitor page state
	this.check_page_state = function() {
		$(window).on('beforeunload', function() {
			
			// If locked by the current user
			if (lense.admin.handler.edit_state.locked == 'yes' && lense.admin.handler.edit_state.locked_by == lense.api.client.params.user) {
				lense.method['handler.close_confirm']({'uuid': lense.admin.handler.active()});
			}
		});
	}
	
	/**
	 * Construct Request Data
	 */
	this.construct_request = function() {
		
		// Request data
		var data = {
			rmap: (function() {
				return lense.admin.handler.window.getSession().getValue().replace(/(\r\n|\n|\r|\t)/gm,"");
			})()
		};
		
		// <input> elements
		$('input[form="edit_handler"]').each(function(i,o) {
			var a = get_attr(o);
			if (!a.hasOwnProperty('ignore')) {
				data[a.name] = $(o).val();
			}
		});
		
		// <select> elements
		$('select[form="edit_handler"]').each(function(i,o) {
			var a = get_attr(o);
			
			// multiple
			if (a.hasOwnProperty('multiple')) {
				var s = [];
				$.each($(o).find('option:selected'), function(i,o) {
					s.push($(o).val());
				});
				data[a.name] = s;
				
			// single
			} else {
				var s = $(o).find('option:selected').val();
				
				// Extract any boolean values
				if (s.indexOf('bool:') >= 0) {
					b = s.split(':');
					s = (b[1] === 'true') ? true : false;
				}
				data[a.name] = s;
			}
		});
		return data;
	}
	
	/**
	 * Callback: Save Handler
	 */
	lense.register.callback('handler.save', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="saved"]').val('yes');
			$('.edit_menu_info').html('All handler changes saved');
			lense.admin.handler.button_state('toggle', {'act': false, 'tgt': 'handler.validate', 'name': 'Validate'}, function() {
				lense.admin.handler.button_state('toggle', {'act': false, 'tgt': 'handler.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="saved"]').val('no');
			lense.admin.handler.button_state('toggle', {'act': false, 'tgt': 'handler.validate', 'name': 'Validate'}, function() {
				lense.admin.handler.button_state('toggle', {'act': true, 'tgt': 'handler.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Validate Handler
	 */
	lense.register.callback('handler.validate', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="validated"]').val('yes');
			$('.edit_menu_info').html('All handler changes validated');
			lense.admin.handler.button_state('toggle', {'act': false, 'tgt': 'handler.validate', 'name': 'Validate'}, function() {
				lense.admin.handler.button_state('toggle', {'act': true, 'tgt': 'handler.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="validated"]').val('no');
			lense.admin.handler.button_state('toggle', {'act': true, 'tgt': 'handler.validate', 'name': 'Validate'}, function() {
				lense.admin.handler.button_state('toggle', {'act': false, 'tgt': 'handler.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Close Handler
	 */
	lense.register.callback('handler.close', function(c,m,d,a) {
		if (c == 200) {
			lense.admin.handler.state(false);
			window.location = '/admin?panel=handlers&handler=' + encodeURIComponent(lense.admin.handler.active());
		} else {
			lense.admin.handler.state(true);
		}
	});
	
	/**
	 * Callback: Open Handler
	 */
	lense.register.callback('handler.open', function(c,m,d,a) {
		if (c == 200) {
			lense.admin.handler.button_state('switch', {'src': 'handler.open', 'tgt': 'handler.close', 'name': 'Close'}, function() {
				lense.admin.handler.state(true);
			});
		} else {
			lense.admin.handler.state(false);
		}
	});
	
	/**
	 * Method: Save Handler
	 */
	lense.register.method('handler.save', function() {
		lense.layout.loading(true, 'Saving handler changes...', function() {
			lense.api.request.put({
				path: 'handler',
				_data: lense.admin.handler.construct_request(),
				callback: {
					id: 'handler.save'
				}
			});
		});
	});
	
	/**
	 * Method: Validate Handler
	 */
	lense.register.method('handler.validate', function() {
		lense.layout.loading(true, 'Validating handler changes...', function() {
			lense.api.request.put({
				path: 'handler/validate',
				_data: lense.admin.handler.construct_request(),
				callback: {
					id: 'handler.validate'
				}
			});
		});
	});
	
	/**
	 * Method: Close Handler
	 */
	lense.register.method('handler.close', function() {
		saved     = $('input[type$="hidden"][name$="saved"]').val();
		validated = $('input[type$="hidden"][name$="validated"]').val();
		
		// If any unsaved or unvalidated changes are present
		if (saved == 'no' || validated == 'no') {
			lense.layout.popup_toggle(true, 'handler.close_confirm');
		} else {
			lense.layout.loading(true, 'Closing edit mode for handler...', function() {
				lense.api.request.put({
					path: 'handler/close',
					_data: {
						uuid: lense.admin.handler.active()
					},
					callback: {
						id: 'handler.close'
					}
				});
			});
		}
	});
	
	/**
	 * Method: Confirm Close Handler
	 */
	lense.register.method('handler.close_confirm', function() {
		lense.layout.popup_toggle(false, 'handler.close_confirm', false, function() {
			lense.layout.loading(true, 'Closing edit mode for handler...', function() {
				lense.api.request.put({
					path: 'handler/close',
					_data: {
						uuid: lense.admin.handler.active()
					},
					callback: {
						id: 'handler.close'
					}
				});
			});
		});
	});
	
	/**
	 * Method: Open Handler
	 */
	lense.register.method('handler.open', function() {
		lense.layout.loading(true, 'Opening handler for editing...', function() {
			lense.api.request.put({
				path: 'handler/open',
				_data: {
					uuid: lense.admin.handler.active()
				},
				callback: {
					id: 'handler.open'
				}
			});
		});
	});
});