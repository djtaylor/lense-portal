cs.import('CSAdminEndpointDetails', function() {
	
	// Request map
	this.rmap   = null;
	
	// Endpoint name
	this.name   = null;
	
	// Endpoint window
	this.window = null;
	
	// Endpoint state
	this.edit_state = {
		locked: 'no',
		locked_by: undefined
	};
	
	/**
	 * Initialize CSAdminEndpointDetails
	 * @constructor
	 */
	this.__init__ = function() {

		// Load endpoint details
		cs.admin.endpoint.load();

		// Bind button actions
		cs.admin.endpoint.bind();
		
		// Document ready
		$(document).ready(function() {
			cs.admin.endpoint.set_input();
			cs.admin.endpoint.set_dimensions();
			cs.admin.endpoint.set_window();
			cs.admin.endpoint.state();
			cs.admin.endpoint.check_page_state();
		});
		
		// Window resize
		$(window).resize(function() {
			cs.admin.endpoint.set_dimensions();
		});
	}
	
	/**
	 * Bind Button Actions
	 */
	this.bind = function() {
		
		// Jump to another endpoint
		$('select[name="endpoint_jump"]').on('change', function() {
			if (cs.admin.endpoint.active() != this.value) {
				window.location = '/portal/admin?panel=endpoints&endpoint=' + this.value;
			}
		});
	}
	
	/**
	 * Get Activate Endpoint
	 */
	this.active = function() {
		return $('input[type="hidden"][form="edit_endpoint"][name="uuid"]').val(); 
	}
	
	/**
	 * Load Endpoint Request Map
	 */
	this.load = function() {
		
		// Retrieve the endpoint request map and name
		cs.admin.endpoint.rmap = clone(endpoint_rmap);
		cs.admin.endpoint.name = endpoint_name;
		
		// Delete the containing element
		$('#endpoint_load').remove();
	}
	
	/**
	 * Lock Endpoint
	 * 
	 * @param {u} The username that has locked the endpoint.
	 * @param {c} Optional callback function
	 */
	this.lock = function(u,c) {
		cs.admin.endpoint.edit_state = { locked: 'yes', locked_by: u };
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Unlock Endpoint
	 * 
	 * @param {c} Optional callback function
	 */
	this.unlock = function(c) {
		cs.admin.endpoint.edit_state = { locked: 'no', locked_by: undefined };
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
		cs.admin.endpoint.button_state('toggle', {
			act:  true, 
			tgt:  'endpoint.validate', 
			name: 'Validate'
		}, function() {
			cs.admin.endpoint.button_state('toggle', {
				act:  false, 
				tgt:  'endpoint.save', 
				name: 'Save'
			});
		});
	}
	
	/**
	 * Set Input Events
	 */
	this.set_input = function() {
		
		// <input> elements
		$('input[form="edit_endpoint"]').each(function(i,o) {
			$(o).on('change', function() {
				cs.admin.endpoint.changed();
			});
		});
		
		// <select> elements
		$('select[form="edit_endpoint"]').each(function(i,o) {
			$(o).on('change', function() {
				cs.admin.endpoint.changed();
			});
		});
	}
	
	/**
	 * Set Endpoint Dimensions
	 */
	this.set_dimensions = function() {
		edit_height   = ($(window).height() - $('.base_nav').height()) - 20;
		sidebar_width = $('.sidebar').width();
		edit_width    = ($(window).width() - 20);
		header_height = $('.page_header_box').height();
		menu_height   = $('.edit_menu').height();
		editor_height = edit_height - menu_height - header_height - 20;
		
		// Set the editor width and height
		$('.endpoint_edit').height(edit_height);
		$('.editor').height(editor_height);
		$('.endpoint_edit').width(edit_width);
		$('.editor').width(edit_width - sidebar_width - 10);
		$('.sidebar').height(editor_height - 20);
	}
	
	/**
	 * Set Endpoint Window
	 */
	this.set_window = function() {
		
		// Set the mode
		mode = 'ace/mode/json';
		
		// Create the editor instance
		cs.admin.endpoint.window = ace.edit('edit_0');
		cs.admin.endpoint.window.setTheme('ace/theme/chrome');
		cs.admin.endpoint.window.getSession().setMode(mode);
		cs.admin.endpoint.window.getSession().setUseWrapMode(true);
		
		// Set the editor contents
		cs.admin.endpoint.window.setValue(JSON.stringify(cs.admin.endpoint.rmap, null, '\t'), -1);
		
		// Detect if changes have been made and require validation
		cs.admin.endpoint.window.on('change', function(e) {
			cs.admin.endpoint.changed();
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
			cs.admin.endpoint.window.setReadOnly((s === true) ? false : true);
			
			// Set page elements
			if (s === true) {
				cs.admin.endpoint.lock(cs.api.client.params.user, function() {
					cs.url.param_set('edit', 'yes');
					$('.page_title').text(cs.admin.endpoint.name + ' - Edit Endpoint');
					
					// Enable form elements
					$('input[form="edit_endpoint"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
					$('select[form="edit_endpoint"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
				});
			} else {
				cs.admin.endpoint.unlock(function() {
					cs.url.param_set('edit', 'no');
					$('.page_title').text(cs.admin.endpoint.name + ' - View Endpoint');
					
					// Disable form elements
					$('input[form="edit_endpoint"]').each(function(i,o) {
						$(o).attr('disabled', '');
					});
					$('select[form="edit_endpoint"]').each(function(i,o) {
						$(o).attr('disabled', '');
					});
				});
			}
			
		// Check Edit State
		} else {
			
			// Look for the editing parameter
			edit_param = cs.url.param_get('edit');
			
			// If the editing parameter is not set
			if (!defined(edit_param)) {
				if (cs.admin.endpoint.edit_state.locked == 'yes') {
					if (cs.admin.endpoint.edit_state.locked_by == cs.api.client.params.user) {
						cs.method['endpoint.open']({'uuid': cs.admin.endpoint.active()});
					}
				} else { 
					cs.admin.endpoint.state(false); 
				}
			} else {
				if (edit_param == 'yes') {
					cs.method['endpoint.open']({'uuid': cs.admin.endpoint.active()});
				} else { 
					cs.admin.endpoint.state(false); 
				}
			}
		}
	}
	
	// Monitor page state
	this.check_page_state = function() {
		$(window).on('beforeunload', function() {
			
			// If locked by the current user
			if (cs.admin.endpoint.edit_state.locked == 'yes' && cs.admin.endpoint.edit_state.locked_by == cs.api.client.params.user) {
				cs.method['endpoint.close_confirm']({'uuid': cs.admin.endpoint.active()});
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
				return cs.admin.endpoint.window.getSession().getValue().replace(/(\r\n|\n|\r|\t)/gm,"");
			})()
		};
		
		// <input> elements
		$('input[form="edit_endpoint"]').each(function(i,o) {
			var a = get_attr(o);
			if (!a.hasOwnProperty('ignore')) {
				data[a.name] = $(o).val();
			}
		});
		
		// <select> elements
		$('select[form="edit_endpoint"]').each(function(i,o) {
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
	 * Callback: Save Endpoint
	 */
	cs.register.callback('endpoint.save', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="saved"]').val('yes');
			$('.edit_menu_info').html('All endpoint changes saved');
			cs.admin.endpoint.button_state('toggle', {'act': false, 'tgt': 'endpoint.validate', 'name': 'Validate'}, function() {
				cs.admin.endpoint.button_state('toggle', {'act': false, 'tgt': 'endpoint.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="saved"]').val('no');
			cs.admin.endpoint.button_state('toggle', {'act': false, 'tgt': 'endpoint.validate', 'name': 'Validate'}, function() {
				cs.admin.endpoint.button_state('toggle', {'act': true, 'tgt': 'endpoint.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Validate Endpoint
	 */
	cs.register.callback('endpoint.validate', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="validated"]').val('yes');
			$('.edit_menu_info').html('All endpoint changes validated');
			cs.admin.endpoint.button_state('toggle', {'act': false, 'tgt': 'endpoint.validate', 'name': 'Validate'}, function() {
				cs.admin.endpoint.button_state('toggle', {'act': true, 'tgt': 'endpoint.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="validated"]').val('no');
			cs.admin.endpoint.button_state('toggle', {'act': true, 'tgt': 'endpoint.validate', 'name': 'Validate'}, function() {
				cs.admin.endpoint.button_state('toggle', {'act': false, 'tgt': 'endpoint.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Close Endpoint
	 */
	cs.register.callback('endpoint.close', function(c,m,d,a) {
		if (c == 200) {
			cs.admin.endpoint.state(false);
			window.location = '/portal/admin?panel=endpoints&endpoint=' + encodeURIComponent(cs.admin.endpoint.active());
		} else {
			cs.admin.endpoint.state(true);
		}
	});
	
	/**
	 * Callback: Open Endpoint
	 */
	cs.register.callback('endpoint.open', function(c,m,d,a) {
		if (c == 200) {
			cs.admin.endpoint.button_state('switch', {'src': 'endpoint.open', 'tgt': 'endpoint.close', 'name': 'Close'}, function() {
				cs.admin.endpoint.state(true);
			});
		} else {
			cs.admin.endpoint.state(false);
		}
	});
	
	/**
	 * Method: Save Endpoint
	 */
	cs.register.method('endpoint.save', function() {
		cs.layout.loading(true, 'Saving endpoint changes...', function() {
			cs.api.request.post({
				path: 'auth/endpoints',
				action: 'save',
				_data: cs.admin.endpoint.construct_request(),
				callback: {
					id: 'endpoint.save'
				}
			});
		});
	});
	
	/**
	 * Method: Validate Endpoint
	 */
	cs.register.method('endpoint.validate', function() {
		cs.layout.loading(true, 'Validating endpoint changes...', function() {
			cs.api.request.post({
				path: 'auth/endpoints',
				action: 'validate',
				_data: cs.admin.endpoint.construct_request(),
				callback: {
					id: 'endpoint.validate'
				}
			});
		});
	});
	
	/**
	 * Method: Close Endpoint
	 */
	cs.register.method('endpoint.close', function() {
		saved     = $('input[type$="hidden"][name$="saved"]').val();
		validated = $('input[type$="hidden"][name$="validated"]').val();
		
		// If any unsaved or unvalidated changes are present
		if (saved == 'no' || validated == 'no') {
			cs.layout.popup_toggle(true, 'endpoint.close_confirm');
		} else {
			cs.layout.loading(true, 'Closing edit mode for endpoint...', function() {
				cs.api.request.get({
					path: 'auth/endpoints',
					action: 'close',
					_data: {
						uuid: cs.admin.endpoint.active()
					},
					callback: {
						id: 'endpoint.close'
					}
				});
			});
		}
	});
	
	/**
	 * Method: Confirm Close Endpoint
	 */
	cs.register.method('endpoint.close_confirm', function() {
		cs.layout.popup_toggle(false, 'endpoint.close_confirm', false, function() {
			cs.layout.loading(true, 'Closing edit mode for endpoint...', function() {
				cs.api.request.get({
					path: 'auth/endpoints',
					action: 'close',
					_data: {
						uuid: cs.admin.endpoint.active()
					},
					callback: {
						id: 'endpoint.close'
					}
				});
			});
		});
	});
	
	/**
	 * Method: Open Endpoint
	 */
	cs.register.method('endpoint.open', function() {
		cs.layout.loading(true, 'Opening endpoint for editing...', function() {
			cs.api.request.get({
				path: 'auth/endpoints',
				action: 'open',
				_data: {
					uuid: cs.admin.endpoint.active()
				},
				callback: {
					id: 'endpoint.open'
				}
			});
		});
	});
});