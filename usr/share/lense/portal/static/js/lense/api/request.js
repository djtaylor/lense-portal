/**
 * API Request
 *
 * Object designed to handle submitting API request to the Lense
 * Socket.IO proxy server.
 */
lense.import('api.request', function() {

	// Submitted requests
	var requests = {};

	/**
	 * Wait for all submitted API requests to complete
	 *
	 * @param {callback} Object An optional callback method
	 */
	this.waitAll = function(callback) {

		// Wait for all values to be true
		requests.values().every(function(val) {
			return (val === true) ? true: false;
		});

		// Optional callback
		if (defined(callback)) {
			callback();
		}
	}

	/**
	 * Submit API Request
	 *
	 * @param {handler} The handler ID to submit the request to
	 * @param {data}    Any additional request data
	 */
	this.submit = function(handler, data, callback) {

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
		requests[handler] = false;
		lense.api.client.emit('apiSubmit', request);
	}
});
