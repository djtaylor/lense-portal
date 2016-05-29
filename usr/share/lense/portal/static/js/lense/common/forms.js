lense.import('common.forms', function() {
	var self = this;
	
	// Forms container
	this.all = {};
	
	/**
	 * Forms Constructor
	 */
	lense.register.constructor('common.forms', function() {
		self.load();
	});
	
	/**
	 * Set Input Value
	 * 
	 * Set the value of an input field and trigger the 'input' event
	 * 
	 * @param {f} The jQuery filter to find the field
	 * @param {v} The value to set
	 */
	this.setInputValue = function(f,v) {
		$(f).val(v).trigger('input');
	}
	
	/**
	 * Input Validator
	 * 
	 * @param {e} Input element to validate using methods in 'validate.js'
	 */
	this.validateInput = function(e) {
		o = get_attr($(e));
		p = self.parent(e);
		if (o.hasOwnProperty('validate') && defined(o['validate'])) {
			v = self.all[p]['inputs'][o.name]['value'];
			
			// If an additional argument is supplied
			if (o.hasOwnProperty('arg')) {
				return (lense.common.validate[o.validate](v,o.arg)) ? true : false;
			} else {
				return (lense.common.validate[o.validate](v)) ? true : false;
			}
		} else { return true; }
	}
	
	/**
	 * Clear Form Error
	 */
	this.clearError = function(id) {
		$('#' + id + '-feedback').css('display', 'none');
		
		// Make sure the submit button is enabled
		$('#' + id + '-submit').removeAttr('disabled');
	}
	
	/**
	 * Show Form Error
	 * 
	 * @param {id}       The parent form ID
	 * @param {message}  The feedback message to display
	 * @param {callback} An optional callback method
	 */
	this.showError = function(id, message, callback) {
		
		// Show the form error box
		$('#' + id + '-feedback').text(message);
		$('#' + id + '-feedback').css('display', 'all');
		
		// Make sure the submit button is disabled
		$('#' + id + '-submit').attr('disabled', 'disabled');
		
		// Run the callback if defined
		if (defined(callback)) {
			callback();
		}
	}
	
	/**
	 * Input Default State
	 * 
	 * @param {id} The ID of the form input
	 */
	this.setInputDefault = function(id) {
		var group = id + '-group';
		
		// Update elements
		$('#' + id).attr('class', 'form-group');
		$('#' + id).find('span').css('display', 'none');
	}
	
	/**
	 * Input Success State
	 * 
	 * @param {id} The ID of the form input
	 */
	this.setInputSuccess = function(id) {
		var group = id + '-group';
		
		// Update elements
		$('#' + group).attr('class', 'form-group has-success has-feedback');
		$('#' + id + '-status').text('(success)');
		$('#' + id + '-icon').attr('class', 'glyphicon glyphicon-ok form-control-feedback');
		$('#' + group).find('span').css('display', 'all');
	}
	
	/**
	 * Input Error State
     *
     * @param {id} The ID of the form input
     */
	this.setInputError = function(id) {
		var group = id + '-group';
		
		// Update elements
		$('#' + group).attr('class', 'form-group has-error has-feedback');
		$('#' + id + '-status').text('(error)');
		$('#' + id + '-icon').attr('class', 'glyphicon glyphicon-remove form-control-feedback');
		$('#' + group).find('span').css('display', 'all');
	}
	
	/**
	 * Set Form Input
	 * 
	 * Method used to refresh the state of a form input field and its relative icon. This
	 * will change the icon state, and the '_error' and 'value' attributes in the global
	 * forms object.
	 * 
	 * @param {parent} The ID string of the parent form
	 * @param {id}     The ID attribute of the input to set
	 * @param {value}  The value to attempt to set
	 * @param {status} The validation status of the element
	 */
	this.setInputStatus = function(parent, id, value, status) {
	
		// Field group / name
		var group = id + '-group';
		var name  = $('#' + group).find('input')[0].name;
		
		// If the value is invalid
		if (status === false) {
			inputMethod = 'setInputError';
			error       = true;
		} else {
			inputMethod = value === undefined ? 'setInputError' : 'setInputSuccess';
			error       = value === undefined ? true : false;
		}
		
		// Update the field
		self[inputMethod](id);
		
		// Update the forms object
		self.all[p]['inputs'][name]['_error'] = error;
		self.all[p]['inputs'][name]['value']  = value;
	}
	
	/**
	 * Check Form Submission
	 * 
	 * Check to see if a form can be submitted in its current state.
	 * 
	 * @param {id} The ID of the form to check
	 */
	this.canSubmit = function(id) {
		var status = true;
		$.each(self.all[id]['inputs'], function(name, attrs) {
			
			// Error state / empty value for required vield
			status = ((attrs._error) ? false : status)
			status = (((attrs.hasOwnProperty('required') && ! defined($('#' + attrs.id).val()))) ? false : status)
		});
		return status;
	}
	
	/**
	 * Filter Form Data
	 * 
	 * Method to process 'filter' tags when submitting an API request generated from
	 * an HTML form. Filter tags must be defined inside the 'form' block which defines
	 * the API request parameters.
	 * 
	 * EXAMPLE: data = lense.forms.filter('add_host', 'api_data', data);
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
		
		// Disable autocomplete for all forms and inputs
		$('form').attr('autocomplete', 'off');
		$('input').attr('autocomplete', 'off');
		
		// Check each form on the page
		$.each($('form'), function(index, form) {
			inputs = $(form).find('input');
			self.all[form.id] = {'id': form.id, 'inputs': {}};
			$.each(inputs, function(index, input) {
				a = get_attr(input);
				disabled = (a.hasOwnProperty('disabled')) ? true: false;
				self.all[form.id]['inputs'][a.name] = {'_error': false, '_parent': form.id, '_disabled': disabled};
				$.each(a, function(key, value) {
					self.all[form.id]['inputs'][a.name][key] = value;
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
							p = self.parent(this);
							
							// If the form can be submitted
							if (self.canSubmit(form.id)) {
								self.clearError(form.id);
							}
							
							// Value is empty
							if (!defined($.trim(v))) {
								self.showError(p, 'Please fill out the required fields...', function() {
									self.setInputStatus(p,input.id, undefined, false);
								});
								
							// Validate the value
							} else {
								self.all[p]['inputs'][input.name]['value'] = v;
								if (self.validateInput(input)) {
									self.setInputStatus(p,input.id, v, true);
									required_set = true;
									$.each(self.all[p]['inputs'], function(key, value) {
										if (value._error === true) {
											required_set = false;
										}
									});
									if (required_set === true) {
										self.showError(p, 'Please fill out the required fields...');
									}
								} else {
									self.setInputStatus(p,input.id, v, false);
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
					p = self.parent(e);
				
				// Get the input type
				type = self.all[p]['inputs'][a.name]['type'];
				
				// Radio group value
				if (type == 'radio') {
					val = $('input[type$="radio"][form$="' + p + '"][name$="' + a.name + '"]:checked').val();
					self.all[p]['inputs'][a.name]['value'] = val;
					
				// Default input value
				} else {
					self.all[p]['inputs'][a.name]['value'] = $(e).val();
				}
				
				// Make sure required elements are set
				if (a.hasOwnProperty('required')) {
					if (! self.all[p]['inputs'][a.name]['_disabled'] === true) {
						if (!defined(self.all[p]['inputs'][a.name]['value'])) {
							_error = a.name;
						}
					}
				}
				
				// If the field is in an error state
				if (self.all[p]['inputs'][a.name]['_error']) {
					_error = a.name;
				}
				
				// Validate the input
				if (! self.validateInput(e)) {
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