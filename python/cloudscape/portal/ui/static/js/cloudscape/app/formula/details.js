cs.import('CSFormulaDetails', function() {

	// Editor Windows
	this.windows = {};
	
	/**
	 * Active Formula Attributes
	 */
	this.active = {
		uuid: clone(formula.uuid),
		name: clone(formula.name)
	};
	
	/**
	 * Initialize CSFormulaDetails
	 * @constructor
	 */
	this.__init__ = function() {

		// Load formula contents
		cs.formula.editor.contents = cs.formula.editor.load();

		// Document ready
		$(document).ready(function() {
			cs.formula.editor.set_dimensions();
			cs.formula.editor.set_windows();
			cs.formula.editor.state();
			cs.formula.editor.resource_toggle();
			cs.formula.editor.check_page_state();
		});
		
		// Window resize
		$(window).resize(function() {
			cs.formula.editor.set_dimensions()
		});
		
		// Jump to another formula
		$('select[name="formula_jump"]').on('change', function() {
			if (cs.formula.editor.active.uuid != this.value) {
				window.location = '/formula?panel=details&formula=' + this.value;
			}
		});
	}
	
	/**
	 * Method: Add Template
	 * 
	 * Add a new template object and editor into the DOM. When the formula is
	 * saved, the new template will be submitted to the database. The filter attribute
	 * is retrieved automatically from the attributes of the button that calls this
	 * method.
	 * 
	 * @param {filter} A JQuery filter used to select the appropriate div
	 */
	cs.register.method('editor.add_template', function(filter) {
		function _template_items(n) {
			
			// New template menu entry
			menu = cs.layout.create.element('div', {
				css: 'sidebar_link_optional',
				children: [
				    cs.layout.create.element('div', {
				    	css:  'sidebar_link_inactive sidebar_link_optional_text',
				    	attr: {
				    		type:     'resource',
				    		optional: '',
				    		active:   'no',
				    		name:     n
				    	},
				    	text: 'Template: ' + n
				    }),
				    cs.layout.create.element('div', {
				    	css: 'sidebar_link_optional_check',
				    	children: [
				    	    cs.layout.create.element('input', {
				    	    	attr: {
				    	    		type:  'radio',
				    	    		name:  'template',
				    	    		value: n
				    	    	}
				    	    })           
				    	]
				    })
				]
			});
			
			// New template editor
			cs.formula.editor.contents.template.count++;
			editor = cs.layout.create.element('div', {
				css:  'editor',
				attr: {
					editor: '',
					type:   'template',
					name:   n,
					style: 'display:none;'
				},
				id:   'edit_' + cs.formula.editor.contents.template.count,
			});
			
			// Return the new template objects collection
			return { 'm': menu, 'e': editor }
		}
		
		// Validate and add the template
		$(filter).on('input add', function(e) {
			var v = $(filter).val();
			if (v != '') {
				if (cs.formula.editor.contents.template.list.indexOf(v) > -1) {
					cs.layout.show_response(true, {
						tgt: 'add_template', 
						msg: 'That template name is already taken...' 
					});
				} else {
					cs.layout.show_response(false, { 
						tgt: 'add_template' 
					}, function() {
						if (e.type == 'add') {
							cs.layout.popup_toggle(false, false, false, function() {
								$(filter).val(null);
								
								// Check if restoring a previously deleted template
								if (cs.formula.editor.contents.template.del.indexOf(v) > -1) {
									li = cs.formula.editor.contents.template.del.indexOf(v);
									cs.formula.editor.contents.template.del.splice(li, 1);
								}
								
								// Update the global template objects
								cs.formula.editor.contents.template.list.push(v);
								cs.formula.editor.contents.template.contents[v] = btoa('{# Your new CloudScape Django template #}');
								
								// Construct the new template elements
								ti = _template_items(v);
								
								// Append the new menu and editor
								$('.editor_frame').append(ti['e']);
								$('div[type$="group"][name$="templates"]').append(ti['m']);
								
								// Update the page dimensions and set up the editors
								cs.formula.editor.set_dimensions();
								cs.formula.editor.set_windows();
								$(filter).unbind();
							});
						}
					});
				}
			} else { 
				cs.layout.show_response(true, {
					tgt: 'add_template', 
					msg: 'You must enter a template name...' 
				}); 
			}
		});
		
		// Trigger the initial form check
		$(filter).trigger('add');
	});

	/**
	 * Method: Delete Template
	 * 
	 * Delete a template object and editor from the DOM. When the formula is save,
	 * the API will process the delete flag in the request, and remove the template
	 * from the database.
	 * 
	 * @param {filter} The JQuery filter used select the ID of the template to delete
	 */
	cs.register.method('editor.delete_template', function(filter) {
		var v = $(filter).val();
		if (!defined(v)) {
			cs.layout.render('info', 'You must select a template to delete');
		} else {
			cs.layout.loading(true, 'Deleting formula contents...', function() {
				
				// Get the editor and menu properties
				ep = get_attr($('div[editor][type$="template"][name$="' + v + '"]'));
				mp = get_attr($('div[type$="resource"][name$="' + v + '"]'));
				
				// By setting the 'delete' value for the template object, the API will read
				// this and remove it from the database.
				
				// Delete from the global templates object
				li = cs.formula.editor.contents.template.list.indexOf(v);
				cs.formula.editor.contents.template.list.splice(li, 1);
				cs.formula.editor.contents.template.contents[v] = 'delete';
				cs.formula.editor.contents.template.count--;
				
				// Add to the deleted templates list
				cs.formula.editor.contents.template.del.push(v)
				
				// If the resource is active, toggle to the formula
				if (mp.active == 'yes') {
					$('div[type$="resource"][name$="' + cs.formula.editor.active.uuid + '"]').click();
				}
				
				// Delete the menu item and editor
				$('div[editor][id$="' + ep.id + '"]').remove();
				$($('div[type$="resource"][name$="' + value + '"]').parent()).remove();
				cs.layout.loading(false);
			});
		}
	});

	/**
	 * Callback: Validate Formula
	 */
	cs.register.callback('editor.validate', function(c,m,d,a) {
		if (c == 200) {
			$('input[name$="validated"]').val('yes');
			$('.formula_edit_menu_info').html('All formula changes have been validated');
			cs.formula.editor.button_state('toggle', {'act': false, 'tgt': 'editor.validate', 'name': 'Validate'}, function() {
				cs.formula.editor.button_state('toggle', {'act': true, 'tgt': 'editor.save', 'name': 'Save'});
			});
		} else {
			cs.formula.editor.button_state('toggle', {'act': true, 'tgt': 'editor.validate', 'name': 'Validate'}, function() {
				cs.formula.editor.button_state('toggle', {'act': false, 'tgt': 'editor.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Method: Validate Formula
	 * 
	 * Submit formula manifest and templates to the API server for validation. Manifest
	 * JSON validity and structure are checked. Right now there is no template validation.
	 */
	cs.register.method('editor.validate', function() {
		cs.layout.loading(true, 'Validating formula changes...', function() {
			cs.api.request.post({
				path: 'editor',
				action: 'validate',
				_data: cs.formula.editor.construct_request(),
				callback: {
					id: 'editor.validate'
				}
			});
		});
	});

	/**
	 * Callback: Save Formula
	 */
	cs.register.callback('editor.save', function(c,m,d,a) {
		if (c == 200) {
			$('input[name$="saved"]').val('yes');
			$('.formula_edit_menu_info').html('All formula changes have been saved');
			cs.formula.editor.button_state('toggle', {'act': false, 'tgt': 'editor.validate', 'name': 'Validate'}, function() {
				cs.formula.editor.button_state('toggle', {'act': false, 'tgt': 'editor.save', 'name': 'Save'});
			});
		} else {
			cs.formula.editor.button_state('toggle', {'act': false, 'tgt': 'editor.validate', 'name': 'Validate'}, function() {
				cs.formula.editor.button_state('toggle', {'act': true, 'tgt': 'editor.save', 'name': 'Save'});
			});
		}
	});
	
	/**
	 * Method: Save Formula
	 * 
	 * Submit the formula object in the DOM to the API for saving. The formula manifest
	 * and template files will be Bas64 encoded and sent off to the API.
	 */
	cs.register.method('editor.save', function() {
		cs.layout.loading(true, 'Saving formula changes...', function() {
			cs.api.request.post({
				path: 'editor',
				action: 'save',
				_data: cs.formula.editor.construct_request(),
				callback: {
					id: 'editor.save'
				}
			});
		});
	});

	/**
	 * Callback: Open Formula
	 */
	cs.register.callback('editor.open', function(c,m,d,a) {
		if (c == 200) {
			$('.formula_edit_menu_info').html('Currently editing formula');
			cs.formula.editor.button_state('switch', {'src': 'editor.open', 'tgt': 'editor.close', 'name': 'Close'}, function() {
				cs.formula.editor.state(true);
				$('#edit_only').css('display', 'block');
			});
		} else {
			cs.formula.editor.state(false);
		}
	});
	
	/**
	 * Method: Open Formula
	 * 
	 * Open a formula for editing. This will lock the contents of the target formula and
	 * will prevent other users from making changes to the manifest and templates.
	 */
	cs.register.method('editor.open', function() {
		cs.layout.loading(true, 'Opening formula for editing...', function() {
			cs.api.request.get({
				path: 'editor',
				action: 'open',
				_data: {
					uuid: cs.formula.editor.active.uuid
				},
				callback: {
					id: 'editor.open'
				}
			});
		});
	});

	/**
	 * Callback: Close Formula
	 */
	cs.register.callback('editor.close', function(c,m,d,a) {
		if (c == 200) {
			$('.formula_edit_menu_info').html('Currently viewing formula');
			cs.formula.editor.state(false);
			window.location = '/formula?panel=details&formula=' + cs.formula.editor.active.uuid;
		} else {
			cs.formula.editor.state(true);
		}
	});
	
	/**
	 * Method: Close Formula
	 * 
	 * Check in a formula so that other users can edit. This will remove the lock on the
	 * formula manifest and templates in the database.
	 */
	cs.register.method('editor.close', function() {
		saved     = $('input[type$="hidden"][name$="saved"]').val();
		validated = $('input[type$="hidden"][name$="validated"]').val();
		
		// If any unsaved or unvalidated changes are present
		if (saved == 'no' || validated == 'no') {
			cs.layout.popup_toggle(true, 'editor.close_confirm');
		} else {
			cs.layout.loading(true, 'Closing edit mode for formula...', function() {
				cs.api.request.get({
					path: 'editor',
					action: 'close',
					_data: {
						uuid: cs.formula.editor.active.uuid
					},
					callback: {
						id: 'editor.close'
					}
				});
			});
		}
	});

	/**
	 * Method: Confirm Close Formula
	 * 
	 * If any unsaved or unvalidated changes exist in the formula contents, prompt the
	 * user to confirm before closing.
	 */
	cs.register.method('editor.close_confirm', function() {
		cs.layout.popup_toggle(false, 'editor.close_confirm', false, function() {
			cs.layout.loading(true, 'Closing edit mode for formula...', function() {
				cs.api.request.get({
					path: 'editor',
					action: 'close',
					_data: {
						uuid: cs.formula.editor.active.uuid
					},
					callback: {
						id: 'editor.close'
					}
				});
			});
		});
	});
	
	/**
	 * Construct Request Data
	 * 
	 * Helper method to parse the template objects currently in the DOM and construct
	 * the JSON request body for any of the formula API methods.
	 */
	this.construct_request = function() {
		
		// Encode the formula manfiest
		f_raw      = cs.formula.editor.windows[cs.formula.editor.active.uuid].getSession().getValue();
		f_manifest = f_raw.replace(/\s+/g, ' ');
		f_encoded  = btoa(f_manifest);
		
		// Merge the current and deleted template arrays
		var t_all = cs.formula.editor.contents.template.list.concat(cs.formula.editor.contents.template.del);
		
		// Load each template into the request body
		t_contents = {};
		$.each(t_all, function(i,v) {
			if (!defined(v)) {
				return true;
			}
			t_raw = cs.formula.editor.windows[v].getSession().getValue();
			
			// If deleting the template
			if (cs.formula.editor.contents.template.contents[v] == 'delete') {
				t_contents[v] = cs.formula.editor.contents.template.contents[v];
			
			// Base64 encode the template contents
			} else {
				t_contents[v] = btoa(t_raw);
			}
		});
		
		// Construct the formatted and encoded data object
		f_obj = {
			uuid:     cs.formula.editor.active.uuid,
			manifest: f_encoded	
		}
		if (!$.isEmptyObject(t_contents)) {
			f_obj['templates'] = t_contents
		}
		
		// Return the formatted and encoded data object
		return f_obj
	}
	
	/**
	 * Set Editor Dimensions
	 */
	this.set_dimensions = function() {
		edit_height   = ($(window).height() - $('.base_nav').height()) - 20;
		sidebar_width = $('.sidebar').width();
		edit_width    = ($(window).width() - 20);
		header_height = $('.page_header_box').height();
		menu_height   = $('.formula_edit_menu').height();
		editor_height = edit_height - menu_height - header_height - 20;
		
		// Set the editor width and height
		$('.formula_edit').height(edit_height);
		$('.editor').height(editor_height);
		$('.formula_edit').width(edit_width);
		$('.editor').width(edit_width - sidebar_width - 10);
		$('.sidebar').height(editor_height - 20);
		
		// Optional template links
		$('.sidebar_link_optional_text').width($('div[type$="group"][name$="templates"]').width() - $('.sidebar_link_optional_check').width() - 20);
	}
	
	/**
	 * Switch Button States
	 * 
	 * Helper method to change button states for editor buttons.
	 */
	this.button_state = function(t,p,cb) {
		if (t != 'switch' && t != 'toggle') { return false; }
		if (t == 'toggle') {
			c = p['act'] === true ? 'formula_edit_menu_button_active' : 'formula_edit_menu_button_inactive';
			s = p['act'] === true ? 'yes' : 'no';
			$('div[type$="button"][target$="' + p['tgt'] + '"]').replaceWith('<div class="' + c + '" type="button" action="method" target="' + p['tgt'] + '" active="' + s + '">' + p['name'] + '</div>');
		}
		if (t == 'switch') {
			$('div[type$="button"][target$="' + p['src'] + '"]').replaceWith('<div class="formula_edit_menu_button_active" type="button" action="method" target="' + p['tgt'] + '" active="yes">' + p['name'] + '</div>');
		}
		if (cb) { cb(); }
	}
	
	/**
	 * Resource Buttons
	 */
	this.resource_toggle = function() {
		function _toggle_resource(r) {
			$.each(r, function(index, obj) {
				t = $('div[type$="resource"][name$="' + obj.n + '"]').text();
				a = obj.a ? 'yes': 'no';
				c = obj.a ? 'sidebar_link_active': 'sidebar_link_inactive';
				
				// Switch the buttons depending on the type
				if (obj.o) {
					e = '<div class="' + c + ' sidebar_link_optional_text" type="resource" optional="" active="' + a + '" name="' + obj.n + '">' + t + '</div>';
				} else {
					e = '<div class="' + c + '" type="resource" active="' + a + '" name="' + obj.n +'">' + t + '</div>';
				}
				
				// Replace the div contents
				$('div[type$="resource"][name$="' + obj.n + '"]').replaceWith(e);
			});
			
			// Fade out the active editor and fade in the toggled editor
			$('div[editor][name$="' + r.a.n + '"]').fadeOut(function() {
				$('div[editor][name$="' + r.i.n + '"]').fadeIn('fast');
			});
			
			// Reset the page dimensions
			cs.formula.editor.set_dimensions();
		}
		
		// Handle clicks on resource links
		$(document).on('click', 'div[type$="resource"][active$="no"]', function(e) { 
			
			// Get the inactive and active link attributes
			i = get_attr(e);
			a = get_attr($('div[type$="resource"][active$="yes"]'));
			console.log(i);
			console.log(a);
			
			// Check if the either link is optional
			io = i.hasOwnProperty('optional') ? true: false;
			ao = a.hasOwnProperty('optional') ? true: false;
			
			// Switch the resource editor link and window
			_toggle_resource({i: {n: i.name, o: io, a: true}, a: {n: a.name, o: ao, a: false}});
		});
	}
	
	/**
	 * Edit State
	 * 
	 * If a state parameter is supplied, set the current editing state. If no parameter is
	 * supplied, check the current editing state and set page elements accordingly.
	 * 
	 * @param {s} The editing state
	 */
	this.state = function(s) {
		
		// Set Edit State
		if (defined(s) || s === false) {
			
			// Toggle readonly depending on the state
			$.each(cs.formula.editor.windows, function(key, obj) {
				readonly = s === true ? false : true;
				this.setReadOnly(readonly);
			});
			
			// Set page elements
			if (s === true) {
				cs.formula.editor.lock(cs.api.client.params.user, function() {
					cs.url.param_set('edit', 'yes');
					$('.page_title').text(cs.formula.editor.active.name + ' - Edit Formula');
					$('div[edit_only$="yes"]').fadeIn('fast');
				});
			} else {
				cs.formula.editor.unlock(function() {
					cs.url.param_set('edit', 'no');
					$('.page_title').text(cs.formula.editor.active.name + ' - View Formula');
					$('div[edit_only$="yes"]').fadeOut('fast');
				});
			}
			
		// Check Edit State
		} else {
			
			// Look for the editing parameter
			edit_param = cs.url.param_get('edit');
			
			// If the editing parameter is not set
			if (!defined(edit_param)) {
				if (cs.formula.editor.contents.state.locked == 'yes') {
					if (cs.formula.editor.contents.state.locked_by == cs.api.client.params.user) {
						cs.method['editor.open']({'uuid': cs.formula.editor.active.uuid});
					}
				} else { cs.formula.editor.state(false); }
			} else {
				if (edit_param == 'yes') {
					cs.method['editor.open']({'uuid': cs.formula.editor.active.uuid});
				} else { cs.formula.editor.state(false); }
			}
		}
		
	}
	
	/**
	 * Set Editor Windows
	 * 
	 * Method called on page load, as well as the creation and deletion of templates in the current
	 * DOM. This will reload the ACE editor windows.
	 */
	this.set_windows = function() {
		
		// Load up the editor for each resource
		$('div[editor]').each(function(key, e) {
			a = get_attr(e);
			
			// Set the mode
			mode = a.type == 'formula' ? 'ace/mode/json' : 'ace/mode/django';
			
			// Create the editor instance
			cs.formula.editor.windows[a.name] = ace.edit(a.id);
			cs.formula.editor.windows[a.name].setTheme('ace/theme/chrome');
			cs.formula.editor.windows[a.name].getSession().setMode(mode);
			cs.formula.editor.windows[a.name].getSession().setUseWrapMode(true);
			
			// Set the editor contents
			if (a.type == 'formula') {
				cs.formula.editor.windows[a.name].setValue(JSON.stringify(cs.formula.editor.contents.manifest, null, '\t'), -1);
			} else {
				cs.formula.editor.windows[a.name].setValue(atob(cs.formula.editor.contents.template.contents[a.name]), -1);
			}
		});
		
    	// Detect if changes have been made and require re-validation
		$.each(cs.formula.editor.windows, function(key, obj) {
			this.on('change', function(e) {
				$('input[name$="saved"]').val('no');
	    		$('input[name$="validated"]').val('no');
	    		
	    		// Change value in the menu info div
	    		$('.formula_edit_menu_info').html('You must validate changes before saving');
	    		
	    		// Switch classes on the buttons
	    		cs.formula.editor.button_state('toggle', {
	    			act:  true, 
	    			tgt:  'editor.validate', 
	    			name: 'Validate'
	    		}, function() {
					cs.formula.editor.button_state('toggle', {
						act:  false, 
						tgt:  'editor.save', 
						name: 'Save'
					});
				});
			});
		});
	}
	
	/**
	 * Lock Editor
	 * 
	 * Method used to lock a formula for editing. Sets the contents state object
	 * with the user who has the formula checked out.
	 * 
	 * @param {u} The username that has locked the formula.
	 * @param {c} Optional callback function
	 */
	this.lock = function(u,c) {
		cs.formula.editor.contents.state = { locked: 'yes', locked_by: u };
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Unlock Editor
	 * 
	 * Change the state of a formula to unlocked.
	 * 
	 * @param {c} Optional callback function
	 */
	this.unlock = function(c) {
		cs.formula.editor.contents.state = { locked: 'no', locked_by: undefined };
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Load Formula Contents
	 * 
	 * Load formula contents rendered on the page into memory when the document is loaded,
	 * then delete the containing script element.
	 */
	this.load = function() {
		
		// Formula manifest / state
		f_manifest = clone(formula.manifest);
		f_state    = clone(formula.state);
		
		// Template contents / list / count 
		t_contents = clone(template.encoded);
		t_list     = clone(formula.templates);
		t_count    = $(t_list).length;
		
		// Delete the containing element
		$('#formula_load').remove();
		
		// Construct and return the formula contents object
		return {
			manifest: f_manifest,
			state:	  f_state,
			template: {
				contents: t_contents,
				list:     t_list,
				count:    t_count,
				del:      []  
			}
		};
	}
	
	// Monitor page state
	this.check_page_state = function() {
		$(window).on('beforeunload', function() {
			
			// If locked by the current user
			if (cs.formula.editor.contents.state.locked == 'yes' && cs.formula.editor.contents.state.locked_by == cs.api.client.params.user) {
				cs.method['editor.close_confirm']({'uuid': cs.formula.editor.active.uuid});
			}
		});
	}
});