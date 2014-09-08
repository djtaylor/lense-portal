cs.import('CSAdminGroupDetails', function() {
	
	// Active group
	this.active = cs.url.param_get('group');
	
	/**
	 * Initialize CSAdminGroupDetails
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			$('.table_50').animate({opacity: '1.0'}, 1000);
		});
		
		// Bind events
		cs.admin.groups.bind();
	}
	
	/**
	 * ACL Controls
	 */
	this.acl = {
		update: function(a,e,s,c) {
			cs.api.request.post({
				path:   'group',
				action: 'update',
				_data:  {
					uuid: cs.admin.groups.active,
					permissions: (function() {
						var _p = {};
						_p[a.acl_type] = {};
						if (a.hasOwnProperty('acl_object')) {
							_p[a.acl_type][a.acl_object] = {};
							_p[a.acl_type][a.acl_object][a.acl_object_id] = {};
							_p[a.acl_type][a.acl_object][a.acl_object_id][a.acl_uuid] = s;
						} else {
							_p[a.acl_type][a.acl_uuid] = s;
						}
						return _p;
					})()
				},
				callback: {
					id: c,
					args: {
						acl_type: a.acl_type,
						acl_uuid: a.acl_uuid,
						acl_object_id: (a.hasOwnProperty('acl_object_id')) ? a.acl_object_id : false,
						acl_object: (a.hasOwnProperty('acl_object')) ? a.acl_object : false
					},
					silent: true
				}
			});
		}
	}
	
	/**
	 * Bind Events
	 */
	this.bind = function() {
		
		// Change Protected State
		$('select[name="protected"]').on('change', function() {
			var state = ($(this).val() === 'true') ? true : false;
			cs.layout.loading(true, 'Changing group protected state...', function() {
				cs.api.request.post({
					path:   'group',
					action: 'update',
					_data: (function() {
						var b = { uuid: cs.admin.groups.active };
						b['protected'] = state;
						return b;
					})(),
					callback: {
						id: 'group.update_protected',
						args: (function() {
							var b = {};
							b['protected'] = state;
						})()
					}
				});
			});
		});
		
		// Toggle Allowed Flag
		$('select[name="acl_allow"]').on('change', function() {
			var a = get_attr(this);
			var e = $(this);
			
			// Allow ACL
			if (e.val() == 'yes') {
				cs.layout.loading(true, 'Enabling ACL...', function() {
					cs.admin.groups.acl.update(a,e,true,'group.allow_acl');
				});
				
			// Unallow ACL
			} else {
				cs.layout.loading(true, 'Disabling ACL...', function() {
					cs.admin.groups.acl.update(a,e,false,'group.allow_acl');
				});
			}
		});
		
		// Toggle ACLs
		$('input[type="checkbox"][name="acl_toggle"]').change(function() {
			var a = get_attr(this);
			var e = $(this);
			
			// Enable ACL
			if (e.is(':checked')) {
				cs.layout.loading(true, 'Enabling ACL...', function() {
					cs.admin.groups.acl.update(a,e,true,'group.enable_acl');
				});
				
			// Disable ACL
			} else {
				cs.layout.loading(true, 'Disabling ACL...', function() {
					cs.admin.groups.acl.update(a,e,'remove','group.disable_acl');
				});
			}
		});
	}
	
	/**
	 * Callback: Update Protected State
	 */
	cs.register.callback('group.update_protected', function(c,m,d,a) {
		if (c != 200) {
			$('select[name="protected"]').val(($('select[name="protected"]').val() === 'true') ? 'false' : 'true');
		}
	});
	
	/**
	 * Callback: Unallow ACL
	 */
	cs.register.callback('group.allow_acl', function(c,m,d,a) {
		if (c != 200) {
			
			// Define the object allowed filter
			var allowed_filter = (function() {
				var base = 'select[name="acl_allow"][acl_type="' + a.acl_type + '"][acl_uuid="' + a.acl_uuid + '"]';
				if (a.acl_type == 'object') {
					base += '[acl_object="' + a.acl_object + '"][acl_object_id="' + a.acl_object_id + '"]';
				}
				return base;
			})();
			
			// Change the value back to yes
			$(allowed_filter).val('yes');
		}
	});
	
	/**
	 * Callback: Allow ACL
	 */
	cs.register.callback('group.unallow_acl', function(c,m,d,a) {
		if (c != 200) {
			
			// Define the object allowed filter
			var allowed_filter = (function() {
				var base = 'select[name="acl_allow"][acl_type="' + a.acl_type + '"][acl_uuid="' + a.acl_uuid + '"]';
				if (a.acl_type == 'object') {
					base += '[acl_object="' + a.acl_object + '"][acl_object_id="' + a.acl_object_id + '"]';
				}
				return base;
			})();
			
			// Change the value back to no
			$(allowed_filter).val('no');
		}
	});
	
	/**
	 * Callback: Enable ACL
	 */
	cs.register.callback('group.enable_acl', function(c,m,d,a) {
		if (c == 200) {
			
			// Define the object allowed filter
			var allowed_filter = (function() {
				var base = 'select[name="acl_allow"][acl_type="' + a.acl_type + '"][acl_uuid="' + a.acl_uuid + '"]';
				if (a.acl_type == 'object') {
					base += '[acl_object="' + a.acl_object + '"][acl_object_id="' + a.acl_object_id + '"]';
				}
				return base;
			})();
			
			// Toggle the allowed select element
			$(allowed_filter).removeAttr('disabled').val('yes');
			
			// If updating an object type
			if (a.acl_type == 'object') {
				$('div[col="object_enabled"][object_id="' + a.acl_object_id + '"]').removeAttr('disabled').attr('enabled', '');
			}
			
		// Error, uncheck the element
		} else {
			$('input[type="checkbox"][name="acl_toggle"][acl_type="' + a.acl_type + '"][value="' + a.acl_uuid + '"]').prop('checked', false);
		}
	});
	
	/**
	 * Callback: Disable ACL
	 */
	cs.register.callback('group.disable_acl', function(c,m,d,a) {
		if (c == 200) {
			
			// Define the object allowed filter
			var allowed_filter = (function() {
				var base = 'select[name="acl_allow"][acl_type="' + a.acl_type + '"][acl_uuid="' + a.acl_uuid + '"]';
				if (a.acl_type == 'object') {
					base += '[acl_object="' + a.acl_object + '"][acl_object_id="' + a.acl_object_id + '"]';
				}
				return base;
			})();
			
			// Toggle the allowed select element
			$(allowed_filter).attr('disabled', '').val('no');
			
			// If updating an object type
			if (a.acl_type == 'object') {
				var disable = true;
				$('input[type="checkbox"][acl_object_id="' + a.acl_object_id + '"]').each(function(i,e) {
					if ($(e).is(':checked')) {
						disable = false;
					}
				});
				if (disable) {
					$('div[col="object_enabled"][object_id="' + a.acl_object_id + '"]').removeAttr('enabled').attr('disabled', '');
				}
			}
		// Error, re-check element
		} else {
			$('input[type="checkbox"][name="acl_toggle"][acl_type="' + a.acl_type + '"][value="' + a.acl_uuid + '"]').prop('checked', true);
		}
	});
	
	/**
	 * Callback: Remove Member
	 */
	cs.register.callback('group.remove_member', function(c,m,d,a) {
		if (c == 200) {
			
			// Assign the target member
			var member = $('.table_sortable_item[member="' + d.group.member + '"]');
			
			// Update the target member
			member.detach().appendTo('#group_members_available').removeAttr('managed').attr({
				available: '',
				target:    'group.add_member'
			});
			member.find('.table_sortable_icon').attr('icon', 'add');
		}
	});
	
	/**
	 * Method: Remove Member
	 */
	cs.register.method('group.remove_member', function(user) {
		if (defined(user)) {
			cs.layout.loading(true, 'Removing group member...', function() {
				cs.api.request.post({
					path:   'group/member',
					action: 'remove',
					_data:  {
						uuid: cs.admin.groups.active,
						user: user
					},
					callback: {
						id: 'group.remove_member'
					}
				});
			});
		}
	});
	
	/**
	 * Callback: Add Member
	 */
	cs.register.callback('group.add_member', function(c,m,d,a) {
		if (c == 200) {
			
			// Assign the target member
			var member = $('.table_sortable_item[member="' + d.group.member + '"]');
			
			// Update the target member
			member.detach().appendTo('#group_members_managed').removeAttr('available').attr({
				managed: '',
				target:  'group.remove_member'
			});
			member.find('.table_sortable_icon').attr('icon', 'remove');
		}
	});
	
	/**
	 * Method: Add Member
	 */
	cs.register.method('group.add_member', function(user) {
		if (defined(user)) {
			cs.layout.loading(true, 'Adding group member...', function() {
				cs.api.request.post({
					path:   'group/member',
					action: 'add',
					_data:  {
						uuid: cs.admin.groups.active,
						user: user
					},
					callback: {
						id: 'group.add_member'
					}
				});
			});
		}
	});
});