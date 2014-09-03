/**
 * API Response
 * 
 * Object designed to handle response from the API proxy server.
 */
cs.import('CSAPIResponse', function() {
	
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
					cs.layout.loading('update', response.content); 
				}
				
				// Update agent status
				if (response.type == 'agent.status') {
					
					// Update any rendered agent status markers
					$('div[type="agent.status"][host="' + response.content.uuid + '"]').attr('state', response.content.status).text(response.content.status);
					
					// Update any render agent controls
					$('div[type="agent.control"][host="' + response.content.uuid + '"]').find('.agent_control').each(function(i,c) {
						var a = get_attr(c);
						if (a.action == 'start') {
							$(c).attr('active', ((response.content.status == 'RUNNING') ? 'no': 'yes'));
						} else {
							$(c).attr('active', ((response.content.status == 'RUNNING') ? 'yes': 'no'));
						}
					});
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
					cs.layout.loading(false, content.error, function() {
						cs.layout.render('error', content.error.replace('<', '"').replace('"'));
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
									cs.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
								} else {
									if (response.type == 'error' || response.type == 'warn' || response.type == 'fatal') {
										cs.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
									}
								}
							} else {
								cs.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
							}
						} else {
							cs.layout.render(response.type, content.msg.replace('<', '"').replace('"'));
						}
					}
					
					// Run the callback method
					if ((content.hasOwnProperty('callback')) && (content.callback !== false)) {
						cs.layout.loading(false, 'Received successful API response...', function() {
							if (cs.callback.hasOwnProperty(content.callback.id)) {
								return cs.callback[content.callback.id](response.code, content.msg, content._data, content.callback.args);
							} else {
								throw new CallbackNotFound(content.callback.id);
							}
						});
					}
				}
				
			// Catch all for API response handling errors
			} catch (e) {
				console.log(e.stack);
				cs.layout.loading(false, null, function() {
					return false;
				});
			}
		}
	}
});