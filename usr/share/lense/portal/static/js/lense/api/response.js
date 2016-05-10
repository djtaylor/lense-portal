/**
 * API Response
 * 
 * Object designed to handle response from the API proxy server.
 */
lense.import('api.response', function() {
	var self = this;
	
	/**
	 * Default Callback
	 * 
	 * @param {code} The return code
	 * @param {data} The response data
	 */
	lense.common.register.callback('default', function(code,data) {
		lense.api.response.notify(code, data);
	});
	
	/**
	 * API Response Callback
	 */
	lense.common.register.callback('apiResponse', function(d) {
		console.log(d);
		lense.api.response.notify(d.code, d.contents);
	});
	
	/**
	 * API Update Callback
	 */
	lense.common.register.callback('update', function(d) {
		console.log('update');
	});
	
	/**
	 * API Support Callback
	 */
	lense.common.register.callback('getAPISupport', function(d) {
		lense.api.cache.support = d.contents;
	});
	
	/**
	 * Server Version Callback
	 */
	lense.common.register.callback('getServerVersion', function(d) {
		lense.api.server = d.contents;
		console.log(d.contents);
		$('input.socketio-server').val(lense.api.server);
	});
	
	/**
	 * Notify
	 * 
	 * @param {code} The HTTP response code
	 * @param {data} Any response data
	 */
	this.notify = function(code,data) {
		lense.common.layout.notify(self.getNotifyType(code), 'HTTP ' + code + ': ' + data);
	}
	
	/**
	 * Get Notify Type
	 * 
	 * @param {code} The HTTP code to check against
	 */
	this.getNotifyType = function(code) {
		switch(code) {
			case 200:
				return 'info';
			case 500:
				return 'danger';
			default:
				return 'warning';
		}
	}
});