cs.import('CSAdminUsers', function() {
	
	/**
	 * Initialize CSAdminUsers
	 * @constructor
	 */
	this.__init__ = function() {
		var u = cs.url.param_get('user');
		if (defined(u)) {
			cs.method['user.toggle'](u);
		}
		
		// Toggle password type fields
		cs.admin.users.pw_type();
	}
	
	/**
	 * Get Active User
	 * 
	 * If no parameter is supplied, return the active user. If a string parameter
	 * is supplied, set that as the active user.
	 */
	this.active = function(u) {
		if (defined(u)) {
			$('input[type$="hidden"][name$="active_user"]').val(u)
		} else {
			return $('input[type$="hidden"][name$="active_user"]').val();
		}
	};
	
	/**
	 * Password Type
	 * 
	 * Toggle password type fields when creating a new user account.
	 */
	this.pw_type = function() {
		$('select[name="password_type"]').on('change', function() {
			var t = $(this).val();
			var f = ['password', 'password_confirm'];
			if (t == 'auto') {
				$('#password_manual').fadeOut('fast');
				$.each(f, function(i,v) {
					var e = $('input[type="text"][form="create_user"][name="' + v + '"]');
					e.removeAttr('required');
					e.attr('ignore', '');
				});
			} else {
				$('#password_manual').fadeIn('fast');
				$.each(f, function(i,v) {
					var e = $('input[type="text"][form="create_user"][name="' + v + '"]');
					e.removeAttr('ignore');
					e.attr('required', '');
				});
			}
		});
	}
	
	/**
	 * Callback: Render User Details
	 */
	cs.register.callback('user.render_details', function(c,m,d,a) {
		
		// Update the user details window
		$('#user_details').html(cs.layout.create.element('div', {
			attr: {
				id: 'user_details'
			},
			children: [
				cs.admin.obj_profile({
					source: {
						object: m,
						keys: {
							username:   'Username',
							first_name: 'First Name',
							last_name:  'Last Name',
							email:      'Email'
						}
					},
					table: {
						form: 'edit_user',
						name: 'user_profile'
					}
				}),
				cs.admin.obj_table({
					source: {
						object: m.groups,
						keys:   {
							name: 'Name',
				    		uuid: 'UUID',
				    		desc: 'Description'
						},
						select:  false,
						headers: true,
						rows:    true
					},
					table: {
						name:       'user_groups',
						title:      'Group Membership',
						key:        ['user_groups', ['group']],
						form:       'edit_user'
					}
				})
			]
		}));
		
		// Update the username
		$('#user_details_title').text('User Details: ' + m.username);
		
		// Set the URL parameter
		cs.url.param_set('user', m.username);
		
		// Set the enable/disable button
		var ed = $('#enable_disable');
		ed.attr('target', (m.is_active) ? 'user.disable': 'user.enable');
		ed.text((m.is_active) ? 'Disable User': 'Enable User');
		
		// Fade in the action buttons
		$('#user_details_actions').fadeIn('fast');
		
		// Refresh the layout
		cs.layout.refresh();
	});
	
	/**
	 * Reset User Details
	 */
	this.reset_details = function() {
		
		// Update the group name
		$('#user_details_title').text('User Details: ');
		
		// Update the group details window
		$('#user_details').text('Please select a user to view their details...');
	}
	
	/**
	 * Request User Details
	 */
	this.request_details = function() {
		if (defined(cs.admin.users.active())) {
			cs.api.request.get({
				path:   'user',
				action: 'get',
				_data:  {
					username: cs.admin.users.active()
				},
				callback: {
					id: 'user.render_details'
				}
			});
		}
	}
	
	/**
	 * Callback: Create User
	 */
	cs.register.callback('user.create', function(c,m,d,a) {
		console.log(d);
	});
	
	/**
	 * Callback: Reset User Password
	 */
	cs.register.callback('user.reset_password', function(c,m,d,a) {
		console.log(d);
	});
	
	/**
	 * Callback: Disable User
	 */
	cs.register.callback('user.disable', function(c,m,d,a) {
		var ed = $('#enable_disable');
		ed.attr('target', 'user.enable');
		ed.text('Enable User');
		$('div[type="row"][target="users"][user="' + d.username + '"]').find('div[col="user_enabled"]').text('False');
	});
	
	/**
	 * Callback: Enable User
	 */
	cs.register.callback('user.enable', function(c,m,d,a) {
		var ed = $('#enable_disable');
		ed.attr('target', 'user.disable');
		ed.text('Disable User');
		$('div[type="row"][target="users"][user="' + d.username + '"]').find('div[col="user_enabled"]').text('True');
	});
	
	/**
	 * Method: Delete User Row
	 */
	cs.register.method('user.delete_row', function(d) {
		console.log(d);
	});
	
	/**
	 * Method: Toggle Edit User
	 */
	cs.register.method('user.edit', function() {
		if (defined(cs.admin.users.active())) {
			$.each($('input[form$="edit_user"]'), function(i,e) {
				$(e).removeAttr('readonly');
			});
			$('div[type$="button"][target$="edit_user"]').css('display', 'none');
			$('div[type$="button"][target$="save_user"]').css('display', 'block');
		}
	});
	
	/**
	 * Method: Toggle User
	 */
	cs.register.method('user.toggle', function(u) {
		
		// Check for the active user
		if (u != cs.admin.users.active()) {
			
			// Update the active group
			cs.admin.users.active(u);
			
			// Get new group details
			cs.admin.users.request_details();
		}
	});
	
	/**
	 * Method: Disable User
	 */
	cs.register.method('user.disable', function() {
		var u = cs.admin.users.active();
		if (defined(u)) {
			cs.layout.popup_toggle(false, false, false, function() { 
				cs.api.request.post({
					path:   'user',
					action: 'disable',
					_data:  {
						username: u
					},
					callback: {
						id: 'user.disable'
					}
				});
			});
		}
	});
	
	/**
	 * Method: Enable User
	 */
	cs.register.method('user.enable', function() {
		var u = cs.admin.users.active();
		if (defined(u)) {
			cs.layout.popup_toggle(false, false, false, function() { 
				cs.api.request.post({
					path:   'user',
					action: 'enable',
					_data:  {
						username: u
					},
					callback: {
						id: 'user.enable'
					}
				});
			});
		}
	});
	
	/**
	 * Method: Reset User Password
	 */
	cs.register.method('user.reset_password', function() {
		var u = cs.admin.users.active();
		if (defined(u)) {
			cs.layout.popup_toggle(false, false, false, function() { 
				cs.api.request.post({
					path:   'user',
					action: 'pwreset',
					_data:  {
						username: u
					},
					callback: {
						id: 'user.reset_password'
					}
				});
			});
		}
	});
	
	/**
	 * Method: Create User
	 */
	cs.register.method('user.create', function() {
		
		// Load the request data
		data = {};
		$('input[type="text"][form="create_user"]').each(function(i,o) {
			var a = get_attr(o);
			if (!a.hasOwnProperty('ignore')) {
				data[a.name] = $(o).val();
			}
		});
		
		// Load the initial group UUID
		data['group'] = $('select[form="create_user"][name="group"]').val();
		
		// Submit the API request
		cs.layout.popup_toggle(false, 'user.create', false, function() { 
			cs.layout.loading(true, 'Creating API user...', function() { 
				cs.api.request.post({
					path:   'user',
					action: 'create',
					_data:  data,
					callback: {
						id: 'user.create'
					}
				});
			});
		});
	});
});