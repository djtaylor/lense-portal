cs.import('CSAdminUtilityDetails', function() {
	
	// Request map
	this.rmap   = null;
	
	// Utility name
	this.name   = null;
	
	// Utility window
	this.window = null;
	
	// Utility state
	this.edit_state = {
		locked: 'no',
		locked_by: undefined
	};
	
	/**
	 * Initialize CSAdminUtilityDetails
	 * @constructor
	 */
	this.__init__ = function() {

		// Load utility details
		cs.admin.utility.load();

		// Bind button actions
		cs.admin.utility.bind();
		
		// Document ready
		$(document).ready(function() {
			cs.admin.utility.set_input();
			cs.admin.utility.set_dimensions();
			cs.admin.utility.set_window();
			cs.admin.utility.state();
			cs.admin.utility.check_page_state();
		});
		
		// Window resize
		$(window).resize(function() {
			cs.admin.utility.set_dimensions();
		});
	}
	
	/**
	 * Bind Button Actions
	 */
	this.bind = function() {
		
		// Jump to another utility
		$('select[name="utility_jump"]').on('change', function() {
			if (cs.admin.utility.active() != this.value) {
				window.location = '/admin?panel=utilities&utility=' + this.value;
			}
		});
	}
	
	/**
	 * Get Activate Utility
	 */
	this.active = function() {
		return $('input[type="hidden"][form="edit_utility"][name="uuid"]').val(); 
	}
	
	/**
	 * Load Utility Request Map
	 */
	this.load = function() {
		
		// Retrieve the utility request map and name
		cs.admin.utility.rmap = clone(utility_rmap);
		cs.admin.utility.name = utility_name;
		
		// Delete the containing element
		$('#utility_load').remove();
	}
	
	/**
	 * Lock Utility
	 * 
	 * @param {u} The username that has locked the utility.
	 * @param {c} Optional callback function
	 */
	this.lock = function(u,c) {
		cs.admin.utility.edit_state = { locked: 'yes', locked_by: u };
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Unlock Utility
	 * 
	 * @param {c} Optional callback function
	 */
	this.unlock = function(c) {
		cs.admin.utility.edit_state = { locked: 'no', locked_by: undefined };
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
		cs.admin.utility.button_state('toggle', {
			act:  true, 
			tgt:  'utility.validate', 
			name: 'Validate'
		}, function() {
			cs.admin.utility.button_state('toggle', {
				act:  false, 
				tgt:  'utility.save', 
				name: 'Save'
			});
		});
	}
	
	/**
	 * Set Input Events
	 */
	this.set_input = function() {
		
		// <input> elements
		$('input[form="edit_utility"]').each(function(i,o) {
			$(o).on('change', function() {
				cs.admin.utility.changed();
			});
		});
		
		// <select> elements
		$('select[form="edit_utility"]').each(function(i,o) {
			$(o).on('change', function() {
				cs.admin.utility.changed();
			});
		});
	}
	
	/**
	 * Set Utility Dimensions
	 */
	this.set_dimensions = function() {
		edit_height   = ($(window).height() - $('.base_nav').height()) - 20;
		sidebar_width = $('.sidebar').width();
		edit_width    = ($(window).width() - 20);
		header_height = $('.page_header_box').height();
		menu_height   = $('.edit_menu').height();
		editor_height = edit_height - menu_height - header_height - 20;
		
		// Set the editor width and height
		$('.utility_edit').height(edit_height);
		$('.editor').height(editor_height);
		$('.utility_edit').width(edit_width);
		$('.editor').width(edit_width - sidebar_width - 10);
		$('.sidebar').height(editor_height - 20);
	}
	
	/**
	 * Set Utility Window
	 */
	this.set_window = function() {
		
		// Set the mode
		mode = 'ace/mode/json';
		
		// Create the editor instance
		cs.admin.utility.window = ace.edit('edit_0');
		cs.admin.utility.window.setTheme('ace/theme/chrome');
		cs.admin.utility.window.getSession().setMode(mode);
		cs.admin.utility.window.getSession().setUseWrapMode(true);
		
		// Set the editor contents
		cs.admin.utility.window.setValue(JSON.stringify(cs.admin.utility.rmap, null, '\t'), -1);
		
		// Detect if changes have been made and require validation
		cs.admin.utility.window.on('change', function(e) {
			cs.admin.utility.changed();
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
			cs.admin.utility.window.setReadOnly((s === true) ? false : true);
			
			// Set page elements
			if (s === true) {
				cs.admin.utility.lock(cs.api.client.params.user, function() {
					cs.url.param_set('edit', 'yes');
					$('.page_title').text(cs.admin.utility.name + ' - Edit Utility');
					
					// Enable form elements
					$('input[form="edit_utility"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
					$('select[form="edit_utility"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
				});
			} else {
				cs.admin.utility.unlock(function() {
					cs.url.param_set('edit', 'no');
					$('.page_title').text(cs.admin.utility.name + ' - View Utility');
					
					// Disable form elements
					$('input[form="edit_utility"]').each(function(i,o) {
						$(o).attr('disabled', '');
					});
					$('select[form="edit_utility"]').each(function(i,o) {
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
				if (cs.admin.utility.edit_state.locked == 'yes') {
					if (cs.admin.utility.edit_state.locked_by == cs.api.client.params.user) {
						cs.method['utility.open']({'uuid': cs.admin.utility.active()});
					}
				} else { 
					cs.admin.utility.state(false); 
				}
			} else {
				if (edit_param == 'yes') {
					cs.method['utility.open']({'uuid': cs.admin.utility.active()});
				} else { 
					cs.admin.utility.state(false); 
				}
			}
		}
	}
	
	// Monitor page state
	this.check_page_state = function() {
		$(window).on('beforeunload', function() {
			
			// If locked by the current user
			if (cs.admin.utility.edit_state.locked == 'yes' && cs.admin.utility.edit_state.locked_by == cs.api.client.params.user) {
				cs.method['utility.close_confirm']({'uuid': cs.admin.utility.active()});
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
				return cs.admin.utility.window.getSession().getValue().replace(/(\r\n|\n|\r|\t)/gm,"");
			})()
		};
		
		// <input> elements
		$('input[form="edit_utility"]').each(function(i,o) {
			var a = get_attr(o);
			if (!a.hasOwnProperty('ignore')) {
				data[a.name] = $(o).val();
			}
		});
		
		// <select> elements
		$('select[form="edit_utility"]').each(function(i,o) {
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
	 * Callback: Save Utility
	 */
	cs.register.callback('utility.save', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="saved"]').val('yes');
			$('.edit_menu_info').html('All utility changes saved');
			cs.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				cs.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="saved"]').val('no');
			cs.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				cs.admin.utility.button_state('toggle', {'act': true, 'tgt': 'utility.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Validate Utility
	 */
	cs.register.callback('utility.validate', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="validated"]').val('yes');
			$('.edit_menu_info').html('All utility changes validated');
			cs.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				cs.admin.utility.button_state('toggle', {'act': true, 'tgt': 'utility.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="validated"]').val('no');
			cs.admin.utility.button_state('toggle', {'act': true, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				cs.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Close Utility
	 */
	cs.register.callback('utility.close', function(c,m,d,a) {
		if (c == 200) {
			cs.admin.utility.state(false);
			window.location = '/admin?panel=utilities&utility=' + encodeURIComponent(cs.admin.utility.active());
		} else {
			cs.admin.utility.state(true);
		}
	});
	
	/**
	 * Callback: Open Utility
	 */
	cs.register.callback('utility.open', function(c,m,d,a) {
		if (c == 200) {
			cs.admin.utility.button_state('switch', {'src': 'utility.open', 'tgt': 'utility.close', 'name': 'Close'}, function() {
				cs.admin.utility.state(true);
			});
		} else {
			cs.admin.utility.state(false);
		}
	});
	
	/**
	 * Method: Save Utility
	 */
	cs.register.method('utility.save', function() {
		cs.layout.loading(true, 'Saving utility changes...', function() {
			cs.api.request.post({
				path: 'gateway/utilities/save',
				_data: cs.admin.utility.construct_request(),
				callback: {
					id: 'utility.save'
				}
			});
		});
	});
	
	/**
	 * Method: Validate Utility
	 */
	cs.register.method('utility.validate', function() {
		cs.layout.loading(true, 'Validating utility changes...', function() {
			cs.api.request.post({
				path: 'gateway/utilities/validate',
				_data: cs.admin.utility.construct_request(),
				callback: {
					id: 'utility.validate'
				}
			});
		});
	});
	
	/**
	 * Method: Close Utility
	 */
	cs.register.method('utility.close', function() {
		saved     = $('input[type$="hidden"][name$="saved"]').val();
		validated = $('input[type$="hidden"][name$="validated"]').val();
		
		// If any unsaved or unvalidated changes are present
		if (saved == 'no' || validated == 'no') {
			cs.layout.popup_toggle(true, 'utility.close_confirm');
		} else {
			cs.layout.loading(true, 'Closing edit mode for utility...', function() {
				cs.api.request.get({
					path: 'gateway/utilities/close',
					_data: {
						uuid: cs.admin.utility.active()
					},
					callback: {
						id: 'utility.close'
					}
				});
			});
		}
	});
	
	/**
	 * Method: Confirm Close Utility
	 */
	cs.register.method('utility.close_confirm', function() {
		cs.layout.popup_toggle(false, 'utility.close_confirm', false, function() {
			cs.layout.loading(true, 'Closing edit mode for utility...', function() {
				cs.api.request.get({
					path: 'gateway/utilities/close',
					_data: {
						uuid: cs.admin.utility.active()
					},
					callback: {
						id: 'utility.close'
					}
				});
			});
		});
	});
	
	/**
	 * Method: Open Utility
	 */
	cs.register.method('utility.open', function() {
		cs.layout.loading(true, 'Opening utility for editing...', function() {
			cs.api.request.get({
				path: 'gateway/utilities/open',
				_data: {
					uuid: cs.admin.utility.active()
				},
				callback: {
					id: 'utility.open'
				}
			});
		});
	});
});