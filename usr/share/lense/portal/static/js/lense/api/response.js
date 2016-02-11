/**
 * API Response
 * 
 * Object designed to handle response from the API proxy server.
 */
lense.import('LenseAPIResponse', function() {
	
	/**
	 * Proxy Response Handler
	 * 
	 * Process responses based on type from the API proxy server.
	 * 
	 * @param {t} The response type
	 * @param {r} The response JSON content
	 */
	this.on = function(type,response) {
		
		// Type: Update
		if (type == 'update') {
			try {
				
				// Render loading message
				if (response.type == 'loading') { 
					lense.layout.loading('update', response.content); 
				}
				
			// Catch exceptions
			} catch (e) { 
				return false; 
			}
		}
		
		// Type: Response
		if (type == 'response') {
			try {
				
				// Parse the JSON response
				content = JSON.parse(response.content);
				
				// If an error response was returned
				if (content.hasOwnProperty('error')) {
					lense.layout.loading(false, content.error, function() {
						lense.layout.render('error', content.error.replace('<', '"').replace('"'));
						return false;
					});
					
				// Handle the response
				} else { 
					try {
						content.msg = JSON.parse(content.msg);
					} catch (e) {
						// Message is not JSON parseable
					}
					
					// Render the response message if not JSON
					if (typeof content.msg !== 'object' && typeof content.msg !== 'array') {
						if (content.hasOwnProperty('callback')) {
							if (content.callback.hasOwnProperty('silent')) {
								if (content.callback.silent === false) {
									lense.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
								} else {
									if (response.type == 'error' || response.type == 'warn' || response.type == 'fatal') {
										lense.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
									}
								}
							} else {
								lense.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
							}
						} else {
							lense.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
						}
					}
					
					// Run the callback method
					if ((content.hasOwnProperty('callback')) && (content.callback !== false)) {
						lense.layout.loading(false, 'Received successful API response...', function() {
							if (lense.callback.hasOwnProperty(content.callback.id)) {
								return lense.callback[content.callback.id](response.code, content.msg, content._data, content.callback.args);
							} else {
								throw new CallbackNotFound(content.callback.id);
							}
						});
					}
				}
				
			// Catch all for API response handling errors
			} catch (e) {
				console.log(e.stack);
				lense.layout.loading(false, null, function() {
					return false;
				});
			}
		}
	}
});