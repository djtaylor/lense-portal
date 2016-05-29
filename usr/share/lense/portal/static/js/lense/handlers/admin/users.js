lense.import('admin.users', function() { 
	var self = this;
	
	/**
	 * Load Users Callback
	 */
	lense.register.callback('loadUsers', function(data) {
		$.each(data, function(i,user) {
			$('#users-list').prepend(
				'<tr user="' + user.uuid + '">' +
				'<th scope="row"><input type="checkbox" user="' + user.uuid + '"></th>' +
				'<th>' + user.username + '</th>' +
				'<th>' + user.email + '</th>' +
				'<th>' + user.uuid + '</th>' +
				'</tr>');
		});
	});
	
	/**
	 * Constructor
	 */
	lense.register.constructor('admin.users', function() {
		
		// Load users
		lense.api.request.submit('user_get', null, 'loadUsers');
		
		// Bind events
		self.bind();
	});
	
	/**
	 * Create User
	 */
	this.createUser = function() {
		lense.common.forms.validate('#create-user-form');
		
		// Hide the modal and show the waiting dialog
		//$('#create-user').modal('hide');
		//waitingDialog.show('Creating user...');
	}
	
	/**
	 * Bind Events
	 */
	this.bind = function() {
		
		// Create user
		$(document).on('click', '#create-user-button', function() {
			self.createUser();
		});
	}
});