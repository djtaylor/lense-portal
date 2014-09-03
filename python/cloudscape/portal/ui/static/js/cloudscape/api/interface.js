/**
 * API Interface
 * 
 * Interface object to facilitate interaction with the CloudScape API
 * server. This includes handling API requests and responses, as well as
 * caching API information on each page load.
 */
cs.import('CSAPIInterface', function() {
	
	/**
	 * Initialize APIInterface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Object extensions
		cs.implement('CSAPIClient', 'api.client');
		cs.implement('CSAPIRequest', 'api.request');
		cs.implement('CSAPIResponse', 'api.response');
		cs.implement('CSAPICache', 'api.cache');
		
		// Open the API connection
		cs.api.client.connect();
		
		// Receive incoming connections
		$(document).ready(function() {
			
			// Receive incoming connections
			cs.api.receive();
			
			// Construct API data cache
			cs.api.cache.construct();
		});
	}
	
	/**
	 * Receive Incoming Connections
	 * 
	 * Method used to handle incoming connections from the proxy server.
	 */
	this.receive = function() {
		
		// Failed to establish client connection
		if (cs.api.client.io === false) {
			cs.layout.render('error', 'Failed to initialize API socket client')
			
		// Connection established
		} else {
			console.log('Established connection to CloudScape Socket.IO server')
			
			// Handle incoming connections
			cs.api.client.io.on('connect', function() {
				cs.api.client.io.on('response', function(j) { 
					cs.api.response.on('response', j); 
				});
				cs.api.client.io.on('update', function(j) { 
					cs.api.response.on('update', j);   
				});
			});
			
			// Handle closed connections
			cs.api.client.io.on('disconnect', function() {
				console.log('Close Socket.IO server connection');
			});
		}
	}
});