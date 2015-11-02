lense.import('LenseAPIMConnectorList', function() {
	
	/**
	 * Intialize LenseAPIMConnectorList
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			
		});
		
		// Window resize
		$(window).resize(function() {
			
		});
	}
	
	/**
	 * Callback: Create Connector
	 */
	lense.register.callback('connector.create', function(c,m,d,a) {
		console.log(d);
	});
	
	/**
	 * Callback: Delete Connector
	 */
	lense.register.callback('connector.delete', function(c,m,d,a) {
		lense.layout.remove('div[type="row"][connector="' + d.uuid + '"]');
	});
	
	/**
	 * Method: Create Connector
	 */
	lense.register.method('connector.create', function() {
		
		// Load the request data
		data = {};
		$('input[type="text"][form="create_connector"]').each(function(i,o) {
			var a = get_attr(o);
			if (!a.hasOwnProperty('ignore')) {
				data[a.name] = $(o).val();
			}
		});
		
		// Make the API call
		lense.layout.popup_toggle(false, 'connector.create', false, function() { 
			lense.layout.loading(true, 'Creating API connector...', function() {
				lense.api.request.post({
					path: 'connector',
					_data: data,
					callback: {
						id: 'connector.create'
					}
				});
			});
		});
	})
	
	/**
	 * Method: Delete Connector
	 */
	lense.register.method('connector.delete', function() {
		var s = $('input[type="radio"][name="connector_uuid"]:checked').val();
		if (defined(s)) {
			lense.layout.popup_toggle(false, 'connector.delete', false, function() { 
				lense.layout.loading(true, 'Deleting API connector...', function() {
					lense.api.request.del({
						path: 'connector',
						_data: {
							uuid: s
						},
						callback: {
							id: 'connector.delete'
						}
					});
				});
			});
		}
	})
});