lense.import('admin.handlers', function() { 
	var self = this;
	
	/**
	 * Insert Handler Row
	 */
	this.insertHandlerRow = function(handler) {
		$('#handlers-list').prepend(
			'<tr handler="' + handler.uuid + '">' +
			'<th scope="row"><input type="checkbox" handler="' + handler.uuid + '"></th>' +
			'<th>' + handler.name + '</th>' +
			'<th>' + handler.path + '</th>' +
			'<th>' + handler.method + '</th>' +
			'<th>' + handler['protected'] + '</th>' +
			'<th>' + handler.enabled + '</th>' +
			'</tr>'
		);
	}
	
	/**
	 * Load Handlers Callback
	 */
	lense.register.callback('loadHandlers', function(data) {
		if ($.isArray(data)) {
			$.each(data, function(i,handler) {
				self.insertHandlerRow(handler);
			});
		} else {
			self.insertHandlerRow(data);
		}
	});
	
	/**
	 * Constructor
	 */
	lense.register.constructor('admin.handlers', function() {
		
		// Load users
		lense.api.request.submit('handler_get', null, 'loadHandlers');
		
		// Bind events
		self.bind();
	});
	
	/**
	 * Create Handler
	 */
	this.createUser = function() {
		lense.common.forms.validate('#create-handler-form');
		
		// Hide the modal and show the waiting dialog
		//$('#create-handler').modal('hide');
		//waitingDialog.show('Creating handler...');
	}
	
	/**
	 * Bind Events
	 */
	this.bind = function() {
		
		// Create user
		$(document).on('click', '#create-handler-button', function() {
			self.createHandler();
		});
	}
});