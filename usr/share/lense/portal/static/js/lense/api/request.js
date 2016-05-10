/**
 * API Request
 * 
 * Object designed to handle submitting API request to the Lense
 * Socket.IO proxy server.
 */
lense.import('api.request', function() {
	
	/**
	 * Submit API Request
	 * 
	 * @param {handler} The handler ID to submit the request to
	 * @param {data}    Any additional request data
	 */
	this.submit = function(handler, data, callback) {
		
		// Make sure the handler is valid
		if (!defined(lense.api.cache.handlers[handler])) {
			return console.log('Invalid request handler: ' + handler);
		}
		
		// Get the handler object
		handler = lense.api.cache.handlers[handler];
		
		// Request object
		var request = {
			'auth':     lense.api.client.authentication(),
			'handler':  handler,
			'callback': callback
		};
		
		// If request data is supplied
		if (defined(data)) { 
			request['data'] = data; 
		}
		
		// Submit the request
		lense.api.client.emit('apiSubmit', request);
	}
});