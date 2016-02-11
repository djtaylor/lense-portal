lense.import('Button', function() {
	
	/**
	 * Button Handler
	 * 
	 * Method to handle divs with the attribute button type attribute. Grab the clicked
	 * element, parse out additional attributes, and execute the appropriate command.
	 * Designed to replace seperate methods of click handling in one function.
	 */
	this.handler = function() {
		
		/**
		 * Execute Hover Action
		 */
		function hover_exec(e,a) {
			
			// Toggle Element
			if (a.action == 'menutoggle') {
				child_hover = false
				
				// Wrapper method to toggle menu element
				function _display_toggle(s) {
					setTimeout(function() {
						if (child_hover === false) {
							$('div[type="menutoggle"][name="' + a.target + '"]').css('display', s);
						}
					}, 50);
				}
				
				// Bind to the toggle menu element
				$(document).on('mouseenter mouseleave', 'div[type="menutoggle"][name="' + a.target + '"]', function(ce) {
					child_hover = (ce.type == 'mouseenter') ? true : false;
					child_state = (child_hover) ? 'block' : 'none';
					_display_toggle(child_state);
				});
				
				// Toggle Menu Item
				state = (e.type == 'mouseenter') ? 'block' : 'none';
				_display_toggle(state);
			}
		}
		
		/**
		 * Execute Button Action
		 */
		function button_exec(e,a) {
			
			// Toggle Method
			if (a.action == 'method') {
				if (a.hasOwnProperty('require')) {
					if (!defined($(a.require).val())) {
						lense.layout.render('info', 'You must select an option from the list to run this action');
						return false;
					}
				}
				if (lense.method.hasOwnProperty(a.target)) {
					if (a.hasOwnProperty('arg')) { 
						lense.method[a.target](a.arg); 
					} else { 
						lense.method[a.target](); 
					}
				} else {
					throw new MethodNotFound(a.target);
				}
			}
			
			// Update Dropdown
			if (a.action == 'dropdown') {
				$('div[type="toggle"][name="' + a.target + '"]').slideToggle('fast', function() {
					$('div[type="dropdown"][target="' + a.target + '"]').attr('target', a.target).text(a.label);
					lense.forms.set_field('input[type="hidden"][name="' + a.target + '"]', a.value);
				});
				
				// If setting another hidden field
				if (a.hasOwnProperty('set')) {
					set_attr = a.set.split('=')
					lense.forms.set_field('input[type="hidden"][name="' + set_attr[0] + '"]', set_attr[1]);
				}
			}
			
			// Submit Form
			if (a.action == 'submit') { 
				field_check = lense.forms.validate(a.target);
				if (field_check === true) {
					$(a.target).submit(); 
				} else { 
					lense.layout.show_response(true, { tgt: a.target, msg: 'Please fill in the required fields...' }, function() {
						$.each(lense.forms.all[a.target.slice(1)]['inputs'], function(key, obj) {
							if (obj.hasOwnProperty('required') && !defined(obj.value)) {
								lense.forms.set_input(obj._parent, obj.name, undefined);
							}
						});
					});
				}
			}
			
			// Toggle Input Element
			if (a.action == 'toggle_input') {
				var ta = get_attr($(a.target));
				if (ta.hasOwnProperty('disabled')) {
					$('div[action="' + a.action + '"][target="' + a.target + '"]').attr('state', 'enabled');
					$(a.target).removeAttr('disabled');
				} else {
					$('div[action="' + a.action + '"][target="' + a.target + '"]').attr('state', 'disabled');
					$(a.target).attr('disabled', '');
				}
			}
			
			// Toggle Specific Element
			if (a.action == 'toggle') {
				te = $('div[type$="toggle"][name$="' + a.target + '"]'); 
				$(te).slideToggle('fast');
			}
			
			// Group Toggle
			if (a.action == 'grouptoggle') {
				if ($('div[type="grouptoggle"][group="' + a.group + '"][name="' + a.target + '"').css('display') == 'none') {
					$.each($('div[type="grouptoggle"][group="' + a.group + '"]'), function(i,e) {
						$(e).css('display', 'none');
					});
					$.each($('div[type="button"][action="grouptoggle"][group="' + a.group + '"]'), function(i,e) {
						ea = get_attr(e);
						if (ea.target == a.target) {
							$(e).addClass('table_action_active');
							$(e).removeClass('table_action');
						} else {
							$(e).addClass('table_action');
							$(e).removeClass('table_action_active');
						}
					});
					$('div[type="grouptoggle"][group="' + a.group + '"][name="' + a.target + '"').fadeIn('fast');
				}
			}
			
			// Toggle Popup Window
			if (a.action == 'popup') {
				parent = (a.hasOwnProperty('parent')) ? a.parent : null;
				
				// Look for a required input value
				if (a.hasOwnProperty('require')) {
					if (!defined($(a.require).val())) {
						lense.layout.render('info', 'You must select an option from the list to run this action');
					} else { lense.layout.popup_toggle(true, a.target, parent); }
				} else { lense.layout.popup_toggle(true, a.target, parent); }
			}
			
			// Page Link
			if (a.action == 'link') { 
				if (a.hasOwnProperty('require')) {
					if (!defined($(a.require).val())) {
						lense.layout.render('info', 'You must select an option from the list to run this action');
						return false;
					}
				}
				if (a.target.match(/^.*[require].*$/)) {
					v = $(a.require).val();
					t = a.target.replace('[require]', v);
					window.location = t;
				} else if (a.target.match(/^\/.*$/)) {
					if (a.hasOwnProperty('newtab')) {
						window.open(a.target, '_blank');
					} else {
						window.location = a.target;
					}
				} else {
					window.location = '/' + a.target; 
				}
			}
			
			// Toggle Fadeout
			if (a.action == 'fadeout') {
				var targets = a.target.split(',');
				if (a.target.contains('popup')) {
					$('html, body').css({
						overflow: 'auto',
						height:   'auto'
					});
				}
				$.each(targets, function(key, elem) {
					if (elem == 'cs') { 
						$(e.currentTarget).fadeOut('fast'); 
					} else {
						$(elem).fadeOut('fast'); 
					}
				});
			}
		}
		
		/**
		 * Detect Hover Elements
		 */
		$(document).on('mouseenter mouseleave', 'div[type="hover"]', function(e) {
			a = get_attr(e);
			hover_exec(e,a);
		});
		
		/**
		 * Detect Button Click
		 */
		$(document).on('click', 'div[type="button"]', function(e) {
			a = get_attr(e);
			if (a.hasOwnProperty('active')) {
				if (a.active == 'yes') { button_exec(e, a); }
			} else { button_exec(e, a); }
		});
		
		/**
		 * Detect Radio Click
		 */
		$(document).on('click', 'input[type="radio"][action="update"]', function(e) {
			a = get_attr(e);
			if (a.hasOwnProperty('name')) {
				lense.forms.set_field('input[type="hidden"][name="' + a.name + '"]', a.value);
			}
		});
	}
});