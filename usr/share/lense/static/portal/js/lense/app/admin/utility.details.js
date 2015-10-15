lense.import('LenseAdminUtilityDetails', function() {
	
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
	 * Initialize LenseAdminUtilityDetails
	 * @constructor
	 */
	this.__init__ = function() {

		// Load utility details
		lense.admin.utility.load();

		// Bind button actions
		lense.admin.utility.bind();
		
		// Document ready
		$(document).ready(function() {
			lense.admin.utility.set_input();
			lense.admin.utility.set_dimensions();
			lense.admin.utility.set_window();
			lense.admin.utility.state();
			lense.admin.utility.check_page_state();
		});
		
		// Window resize
		$(window).resize(function() {
			lense.admin.utility.set_dimensions();
		});
	}
	
	/**
	 * Bind Button Actions
	 */
	this.bind = function() {
		
		// Jump to another utility
		$('select[name="utility_jump"]').on('change', function() {
			if (lense.admin.utility.active() != this.value) {
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
		lense.admin.utility.rmap = clone(utility_rmap);
		lense.admin.utility.name = utility_name;
		
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
		lense.admin.utility.edit_state = { locked: 'yes', locked_by: u };
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
		lense.admin.utility.edit_state = { locked: 'no', locked_by: undefined };
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
		lense.admin.utility.button_state('toggle', {
			act:  true, 
			tgt:  'utility.validate', 
			name: 'Validate'
		}, function() {
			lense.admin.utility.button_state('toggle', {
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
				lense.admin.utility.changed();
			});
		});
		
		// <select> elements
		$('select[form="edit_utility"]').each(function(i,o) {
			$(o).on('change', function() {
				lense.admin.utility.changed();
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
		lense.admin.utility.window = ace.edit('edit_0');
		lense.admin.utility.window.setTheme('ace/theme/chrome');
		lense.admin.utility.window.getSession().setMode(mode);
		lense.admin.utility.window.getSession().setUseWrapMode(true);
		
		// Set the editor contents
		lense.admin.utility.window.setValue(JSON.stringify(lense.admin.utility.rmap, null, '\t'), -1);
		
		// Detect if changes have been made and require validation
		lense.admin.utility.window.on('change', function(e) {
			lense.admin.utility.changed();
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
			lense.admin.utility.window.setReadOnly((s === true) ? false : true);
			
			// Set page elements
			if (s === true) {
				lense.admin.utility.lock(lense.api.client.params.user, function() {
					lense.url.param_set('edit', 'yes');
					$('.page_title').text(lense.admin.utility.name + ' - Edit Utility');
					
					// Enable form elements
					$('input[form="edit_utility"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
					$('select[form="edit_utility"]').each(function(i,o) {
						$(o).removeAttr('disabled');
					});
				});
			} else {
				lense.admin.utility.unlock(function() {
					lense.url.param_set('edit', 'no');
					$('.page_title').text(lense.admin.utility.name + ' - View Utility');
					
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
			edit_param = lense.url.param_get('edit');
			
			// If the editing parameter is not set
			if (!defined(edit_param)) {
				if (lense.admin.utility.edit_state.locked == 'yes') {
					if (lense.admin.utility.edit_state.locked_by == lense.api.client.params.user) {
						lense.method['utility.open']({'uuid': lense.admin.utility.active()});
					}
				} else { 
					lense.admin.utility.state(false); 
				}
			} else {
				if (edit_param == 'yes') {
					lense.method['utility.open']({'uuid': lense.admin.utility.active()});
				} else { 
					lense.admin.utility.state(false); 
				}
			}
		}
	}
	
	// Monitor page state
	this.check_page_state = function() {
		$(window).on('beforeunload', function() {
			
			// If locked by the current user
			if (lense.admin.utility.edit_state.locked == 'yes' && lense.admin.utility.edit_state.locked_by == lense.api.client.params.user) {
				lense.method['utility.close_confirm']({'uuid': lense.admin.utility.active()});
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
				return lense.admin.utility.window.getSession().getValue().replace(/(\r\n|\n|\r|\t)/gm,"");
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
	lense.register.callback('utility.save', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="saved"]').val('yes');
			$('.edit_menu_info').html('All utility changes saved');
			lense.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				lense.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="saved"]').val('no');
			lense.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				lense.admin.utility.button_state('toggle', {'act': true, 'tgt': 'utility.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Validate Utility
	 */
	lense.register.callback('utility.validate', function(c,m,d,a) {
		if (c == 200) {
			$('input[type$="hidden"][name$="validated"]').val('yes');
			$('.edit_menu_info').html('All utility changes validated');
			lense.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				lense.admin.utility.button_state('toggle', {'act': true, 'tgt': 'utility.save', 'name': 'Save'});
			});
		} else {
			$('input[type$="hidden"][name$="validated"]').val('no');
			lense.admin.utility.button_state('toggle', {'act': true, 'tgt': 'utility.validate', 'name': 'Validate'}, function() {
				lense.admin.utility.button_state('toggle', {'act': false, 'tgt': 'utility.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Callback: Close Utility
	 */
	lense.register.callback('utility.close', function(c,m,d,a) {
		if (c == 200) {
			lense.admin.utility.state(false);
			window.location = '/admin?panel=utilities&utility=' + encodeURIComponent(lense.admin.utility.active());
		} else {
			lense.admin.utility.state(true);
		}
	});
	
	/**
	 * Callback: Open Utility
	 */
	lense.register.callback('utility.open', function(c,m,d,a) {
		if (c == 200) {
			lense.admin.utility.button_state('switch', {'src': 'utility.open', 'tgt': 'utility.close', 'name': 'Close'}, function() {
				lense.admin.utility.state(true);
			});
		} else {
			lense.admin.utility.state(false);
		}
	});
	
	/**
	 * Method: Save Utility
	 */
	lense.register.method('utility.save', function() {
		lense.layout.loading(true, 'Saving utility changes...', function() {
			lense.api.request.post({
				path: 'gateway/utilities/save',
				_data: lense.admin.utility.construct_request(),
				callback: {
					id: 'utility.save'
				}
			});
		});
	});
	
	/**
	 * Method: Validate Utility
	 */
	lense.register.method('utility.validate', function() {
		lense.layout.loading(true, 'Validating utility changes...', function() {
			lense.api.request.post({
				path: 'gateway/utilities/validate',
				_data: lense.admin.utility.construct_request(),
				callback: {
					id: 'utility.validate'
				}
			});
		});
	});
	
	/**
	 * Method: Close Utility
	 */
	lense.register.method('utility.close', function() {
		saved     = $('input[type$="hidden"][name$="saved"]').val();
		validated = $('input[type$="hidden"][name$="validated"]').val();
		
		// If any unsaved or unvalidated changes are present
		if (saved == 'no' || validated == 'no') {
			lense.layout.popup_toggle(true, 'utility.close_confirm');
		} else {
			lense.layout.loading(true, 'Closing edit mode for utility...', function() {
				lense.api.request.get({
					path: 'gateway/utilities/close',
					_data: {
						uuid: lense.admin.utility.active()
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
	lense.register.method('utility.close_confirm', function() {
		lense.layout.popup_toggle(false, 'utility.close_confirm', false, function() {
			lense.layout.loading(true, 'Closing edit mode for utility...', function() {
				lense.api.request.get({
					path: 'gateway/utilities/close',
					_data: {
						uuid: lense.admin.utility.active()
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
	lense.register.method('utility.open', function() {
		lense.layout.loading(true, 'Opening utility for editing...', function() {
			lense.api.request.get({
				path: 'gateway/utilities/open',
				_data: {
					uuid: lense.admin.utility.active()
				},
				callback: {
					id: 'utility.open'
				}
			});
		});
	});
});