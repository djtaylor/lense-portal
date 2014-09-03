/**
 * CloudScape Base Forms Class
 * 
 * Class to handle parsing, validating, and modifying form data in the DOM.
 */
cs.import('CSBaseForms', function() {
	
	// Forms container
	this.all = {};
	
	/**
	 * Create Form Elements
	 */
	this.create = {
		
		/**
		 * Hidden Input
		 * 
		 * Construct a hidden input field.
		 * 
		 * @param {a} The hidden input attributes
		 */
		input_hidden: function(a) {
			a.type = 'hidden';
			return cs.layout.html($('<input/>').attr(a));
		},
		
		/**
		 * Dropdown Menu
		 * 
		 * Construct a custom dropdown menu.
		 * 
		 * @param {p} The dropdown menu parameters
		 */
		dropdown: function(p) {
			
			// Set the menu CSS classes
			var css = {
				option: (function() {
					if (p.type == 'formula') { return 'formula_select_option'; }
				})(),
				field:  (function() {
					if (p.type == 'formula') { return 'formula_field'; }
				})(),
				label:  (function() {
					if (p.type == 'formula') { return 'formula_field_label_dynamic'; }
				})(),
				input:  (function() {
					if (p.type == 'formula') { return 'formula_field_input'; }
				})(),
				icon:   (function() {
					if (p.type == 'formula') { return 'form_input_icon_def'; }
				})()
			}
			
			// Construct the dropdown items
			dd_items = [];
			$.each(p.items, function(k,v) {
				
				// Create the option element
				dd_items.push(cs.layout.create.element('option', {
					css:  css.option,
					attr: {
						value: p.label
					},
					text: k + ':' + v
				}));
				
				// Create the div element
				dd_items.push(cs.layout.create.element('div', {
					css:  'dropdown_item',
					attr: {
						type:   'button',
						action: 'dropdown',
						value:  k,
						label:  k + ':' + v,
						target: p.name
					},
					text: k + ':' + v
				}));
			});
			
			// Construct and return the dropdown menu
			return cs.layout.create.element('div', {
				css:  css.field,
				attr: { 
					name: p.name,
				},
				children: [
				    cs.layout.create.element('div', {
				    	css:  css.label,
				    	text: p.label
				    }),
				    cs.layout.create.element('div', {
				    	css: css.input,
				    	children: [
				    	    cs.layout.create.element('div', {
				    	    	css:  'dropdown_menu',
				    	    	attr: {
				    	    		type:   'dropdown',
				    				target: 'menu',
				    				name:   p.name
				    	    	},
				    	    	children: [
				    	    	    cs.layout.create.element('div', {
				    	    	    	css: 'dropdown_action',
				    	    	    	children: [
				    	    	    	    cs.layout.create.element('div', {
				    	    	    	    	css:  'dropdown_button',
				    	    	    	    	attr: {
				    	    	    	    		type:   'button',
				    	    				    	action: 'toggle',
				    	    				    	target: p.name
				    	    	    	    	}
				    	    	    	    }),
				    	    	    	    cs.layout.create.element('div', {
				    	    	    	    	css:  'dropdown_value',
				    	    	    	    	attr: {
				    	    	    	    		type:   'dropdown',
				    	    				    	target: p.name
				    	    	    	    	},
				    	    	    	    	text: 'Please select...'
				    	    	    	    })
				    	    	    	]
				    	    	    }),
				    	    	    cs.layout.create.element('div', {
				    	    	    	css:  css.icon,
				    	    	    	attr: {
				    	    	    		type: 'icon',
					    					form: p.form,
					    					name: p.name
				    	    	    	}
				    	    	    })
				    	    	]
				    	    }),
				    	    cs.layout.create.element('div', {
				    	    	css:  'dropdown_items',
				    	    	attr: {
				    				type: 'toggle',
				    				name: p.name
				    			},
				    			children: dd_items
				    	    }),
				    	    cs.forms.create.input_hidden({
				    	    	type:  'hidden',
			    				form:  p.form,
			    				name:  p.name,
			    				value: '',
				    	    })
				    	]
				    })
				]
			});
		}
	};
	
	/**
	 * Set Field
	 * 
	 * Set the value of an input field and trigger the 'input' event
	 * 
	 * @param {f} The jQuery filter to find the field
	 * @param {v} The value to set
	 */
	this.set_field = function(f,v) {
		$(f).val(v).trigger('input');
	}
	
	/**
	 * Input Validator
	 * 
	 * @param {e} Input element to validate using methods in 'validate.js'
	 */
	this.validate_input = function(e) {
		o = get_attr($(e));
		p = cs.forms.parent(e);
		if (o.hasOwnProperty('validate') && defined(o['validate'])) {
			v = cs.forms.all[p]['inputs'][o.name]['value'];
			
			// If an additional argument is supplied
			if (o.hasOwnProperty('arg')) {
				return (cs.validate[o.validate](v,o.arg)) ? true : false;
			} else {
				return (cs.validate[o.validate](v)) ? true : false;
			}
		} else { return true; }
	}
	
	/**
	 * Set Form Input
	 * 
	 * Method used to refresh the state of a form input field and its relative icon. This
	 * will change the icon state, and the '_error' and 'value' attributes in the global
	 * forms object.
	 * 
	 * @param {p} The ID string of the parent form
	 * @param {n} The name attribute of the input to set
	 * @param {v} The value to attempt to set
	 * @param {s} The validation status of the element
	 */
	this.set_input = function(p,n,v,s) {
	
		// If the value is invalid
		if (s === false) {
			l = 'err';
			e = true;
		} else {
			l = v === undefined ? 'err' : 'ok';
			e = v === undefined ? true : false;
		}
		
		// Set the target and content for the icon
		t = 'div[type$="icon"][form$="' + p + '"][name$="' + n + '"]';
		c = '<div class="form_input_icon_' + l + '" type="icon" form="' + p + '" name="' + n + '"></div>';
		
		// Update the input icon
		$(t).replaceWith(c);
		
		// Update the forms object
		cs.forms.all[p]['inputs'][n]['_error'] = e;
		cs.forms.all[p]['inputs'][n]['value']  = v;
	}
	
	/**
	 * Filter Form Data
	 * 
	 * Method to process 'filter' tags when submitting an API request generated from
	 * an HTML form. Filter tags must be defined inside the 'form' block which defines
	 * the API request parameters.
	 * 
	 * EXAMPLE: data = cs.forms.filter('add_host', 'api_data', data);
	 * 
	 * @param {f} The identifier string for the form
	 * @param {t} The filter type attribute value
	 * @param {d} The data to filter
	 */
	this.filter = function(f,t,d) {
		$.each($('form[id$="' + f + '"]').find('filter[type$="' + t + '"]'), function(i,filter) {
			fo = get_attr(filter);
			
			// Load any conditionals
			if (fo.hasOwnProperty('if')) {
				ca = fo['if'].split('=');
				if (d[ca[0]] == ca[1]) {
					
					// Exclusions
					if (fo.hasOwnProperty('exclude')) {
						ek = fo['exclude'].split(',');
						$.each(ek, function(i,k) {
							if (d.hasOwnProperty(k) >= 0) {
								delete json_data[k];
							}
						});
					}
				}
			}
		});
		return d;
	}
	
	/**
	 * Load Form Elements
	 * 
	 * Read existing form elements into memory. Used mainly when validating forms, and to
	 * re-check validation status when changing form inputs.
	 */
	this.load = function() {
		
		// Check each form on the page
		$.each($('form'), function(index, form) {
			inputs = $(form).find('input');
			cs.forms.all[form.id] = {'id': form.id, 'inputs': {}};
			$.each(inputs, function(index, input) {
				a = get_attr(input);
				disabled = (a.hasOwnProperty('disabled')) ? true: false;
				cs.forms.all[form.id]['inputs'][a.name] = {'_error': false, '_parent': form.id, '_disabled': disabled};
				$.each(a, function(key, value) {
					cs.forms.all[form.id]['inputs'][a.name][key] = value;
				});
				
				// Skip hidden and non-validating elements
				if (a.type == 'hidden' && ! a.hasOwnProperty('validate')) {
					return true;
				}
				
				// Bind a blur event to each input if not hidden
				if (a.hasOwnProperty('required')) {
					
					// On changes to text input
					if (a.type == 'text' || a.type == 'password' || a.type == 'hidden' || a.type == 'radio') {
						$(input).on('input', function() {
							v = $(this).val();
							p = cs.forms.parent(this);
							if (!defined($.trim(v))) {
								cs.layout.show_response(true, { tgt: p, msg: 'Please fill out the required fields...' }, function() {
									cs.forms.set_input(p,input.name, undefined, false);
								});
							} else {
								cs.forms.all[p]['inputs'][input.name]['value'] = v;
								if (cs.forms.validate_input(input)) {
									cs.forms.set_input(p,input.name, v, true);
									required_set = true;
									$.each(cs.forms.all[p]['inputs'], function(key, value) {
										if (value._error === true) {
											required_set = false;
										}
									});
									if (required_set === true) {
										cs.layout.show_response(false, { tgt: p });
									}
								} else {
									cs.forms.set_input(p,input.name, v, false);
								}
							}
						});
					}
				}
			});
		});
	}
	
	/**
	 * Form Validator
	 * 
	 * Takes a form ID as an argument and makes sure all fields meet submit requirements.
	 * 
	 * @param {id} The ID of the form to validate
	 */
	this.validate = function(id) {
		if ($(id).length) {
			var _error = undefined;
			$.each($(id).find('input'), function(index, obj) {
				var e = $(obj)[0],
					a = get_attr(e),
					p = cs.forms.parent(e);
				
				// Get the input type
				type = cs.forms.all[p]['inputs'][a.name]['type'];
				
				// Radio group value
				if (type == 'radio') {
					val = $('input[type$="radio"][form$="' + p + '"][name$="' + a.name + '"]:checked').val();
					cs.forms.all[p]['inputs'][a.name]['value'] = val;
					
				// Default input value
				} else {
					cs.forms.all[p]['inputs'][a.name]['value'] = $(e).val();
				}
				
				// Make sure required elements are set
				if (a.hasOwnProperty('required')) {
					if (! cs.forms.all[p]['inputs'][a.name]['_disabled'] === true) {
						if (!defined(cs.forms.all[p]['inputs'][a.name]['value'])) {
							_error = a.name;
						}
					}
				}
				
				// If the field is in an error state
				if (cs.forms.all[p]['inputs'][a.name]['_error']) {
					_error = a.name;
				}
				
				// Validate the input
				if (! cs.forms.validate_input(e)) {
					_error = a.name;
				}
			});
			
			// If all required values are set
			if (!defined(_error)) {
				return true;
				
			// If missing the value for a required parameter
			} else {
				console.log(_error);
				return _error;
			}
			
		// If the form ID is not found
		} else { return false; }
	}
	
	/**
	 * Get Parent Form
	 * 
	 * Walk through the parent elements of a specified element, and look
	 * for the first parent tag. If found, return the form ID string.
	 * 
	 * @param {e} The DOM element to do a reverse recursive search from
	 */
	this.parent = function(e) {
		
		// Max recursion and counter
		var max   = 10;
		var count = 0;
		
		// Walk through the element's parent tree
		function _search(e) {
			if (count >= max) {
				return false;
			} else {
				count++;
				p = $(e).parent();
				for (var index in p) {
					if (p[0].localName == 'form') {
						return p[0].id;
					} else {
						return _search(p);
					}
				}
			}
		}
		form = _search(e);
		count = 0;
		return form;
	}
});