lense.import('LenseAdminACLObjectDetails', function() { 
	
	// Active object type
	this.active = lense.url.param_get('object');
	
	/**
	 * Initialize LenseAdminACLObjectDetails
	 * @constructor
	 */
	this.__init__ = function() {}
	
	/**
	 * Callback: Save Object Details
	 */
	lense.register.callback('acl.save_object', function(c,m,d,a) {
		
		// Switch the edit/save buttons
		$('div[type="button"][target="acl.edit_object"]').attr('active', 'yes').css('display', 'block');
		$('div[type="button"][target="acl.save_object"]').attr('active', 'no').css('display', 'none');
		
		// Disable the input fields
		$('input[form="edit_acl_object"]').each(function(i,e) {
			$(e).attr('disabled', '');
		});
		
		// Disable the select fields
		$('select[form="edit_acl_object"]').each(function(i,e) {
			$(e).attr('disabled', '');
		});
	});
	
	/**
	 * Method: Save Object Details
	 */
	lense.register.method('acl.save_object', function() {
		
		// Construct the new object details
		var params = {};
		$('input[form="edit_acl_object"]').each(function(i,o) {
			var a = get_attr(o);
			params[a.name] = a.value;
		});
		
		// Get the default ACL value
		params['def_acl'] = $('select[name="def_acl"]').val();
		
		// Set the active object
		params['type'] = lense.admin.acl_objects.active;
		
		// Submit the API update request
		lense.api.request.put({
			path:     'acl/objects',
			callback: {
				id: 'acl.save_object'
			},
			_data: params
		});
	});
	
	/**
	 * Method: Edit Object Details
	 */
	lense.register.method('acl.edit_object', function() {
			
		// Switch the edit/save buttons
		$('div[type="button"][target="acl.edit_object"]').attr('active', 'no').css('display', 'none');
		$('div[type="button"][target="acl.save_object"]').attr('active', 'yes').css('display', 'block');
		
		// Enable the input fields
		$('input[form="edit_acl_object"]').each(function(i,e) {
			$(e).removeAttr('disabled', '');
		});
		
		// Enable the select fields
		$('select[form="edit_acl_object"]').each(function(i,e) {
			$(e).removeAttr('disabled', '');
		});
	});
	
});