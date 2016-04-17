lense.import('api.interface', function() {
	
	/**
	 * Initialize APIInterface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load modules
		$.each([
		    'api.client',
		    'api.request',
		    'api.response',
		    'api.cache'
		], function(i,k) {
			lense.implement(k);
		});
		
		// Open the API connection
		lense.api.client.connect();
		
		// Receive incoming connections
		$(document).ready(function() {
			
			// Receive incoming connections
			lense.api.receive();
			
			// Construct API data cache
			lense.api.cache.construct();
		});
	}
	
	/**
	 * Receive Incoming Connections
	 * 
	 * Method used to handle incoming connections from the proxy server.
	 */
	this.receive = function() {
		
		// Failed to establish client connection
		if (lense.api.client.io === false) {
			lense.common.layout.render('error', 'Failed to initialize API socket client')
			
		// Connection established
		} else {
			console.log('Established connection to Lense Socket.IO server')
			
			// Handle incoming connections
			lense.api.client.io.on('connect', function() {
				lense.api.client.io.on('response', function(j) { 
					lense.api.response.on('response', j); 
				});
				lense.api.client.io.on('update', function(j) { 
					lense.api.response.on('update', j);   
				});
			});
			
			// Handle closed connections
			lense.api.client.io.on('disconnect', function() {
				console.log('Close Socket.IO server connection');
			});
		}
	}
});