lense.import('api.client', function() {
	
	// Class attributes
	this.params, this.room, this.io;
	
	// Cookie keys
	this.keys = ['user', 'group', 'key', 'token', 'endpoint', 'session'];
	
	/**
	 * Connect APIClient
	 */
	this.connect = function() {
		
		// API connection parameters
		lense.api.client.params = lense.api.client.load_params();
		
		// Client room
		lense.api.client.room   = lense.api.client.params.user + ':' + lense.api.client.params.session;
		
		// Establish API connection
		lense.api.client.io     = lense.api.client.io_connect();
	}
	
	/**
	 * Load API Parameters
	 */
	this.load_params = function() {
		return {
			user: Cookies.get('api_user'),
			url:  Cookies.get('api_endpoint'),
		}
		
		// Clone the parameters
		pr = JSON.parse(JSON.stringify(api_params));
		
		// Delete the page container
		$('#api_params').remove();
		
		// Make sure all the required parameters are set
		ap = function() {
			var pv = true;
			$.each(['user', 'token', 'url', 'session', 'group'], function(i,k) {
				if (!pr.hasOwnProperty(key) || !is_defined(pr[k])) {
					pv = false;
				}
			});
			return pv;
		}
		
		// If all parameters have been read into memory
		return (ap) ? pr : false;
	}
	
	/**
	 * Open Connection
	 * 
	 * Establish a connection to the CloudScape Socket.IO API proxy server
	 * for handling future requests.
	 */
	this.io_connect = function() {
		// Options
		//
		// Set default transports to either 'xhr-polling' or 'jsonp-polling'. There is a bug when
		// using websockets that causes connections on the server to hang in FIN_WAIT2/CLOSE_WAIT
		// state, which quickly uses up all the available file descriptors.
		function options() {
			return {
				secure: (lense.api.client.params.proto == 'https') ? true : false,
				transports: ['xhr-polling', 'jsonp-polling']
			};
		}
		
		// Make sure all required parameters are defined
		if (lense.api.client.params === false) { return false; } 
		
		// Open socket connection
		io_connection = io.connect(lense.api.client.params.url, options())
		
		// Error creating socket connection
		io_connection.on('error', function(e) { return false; });
		
		// Failed to create socket connection
		io_connection.on('connect_failed', function(e) { return false; });
		
		// Join the user to their own room
		io_connection.emit('join', { room: lense.api.client.room });
		
		// Return the connection object
		return io_connection;
	}
});