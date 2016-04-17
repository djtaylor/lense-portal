lense.import('common.register', function() {
	
	/**
	 * Register Callback
	 */
	this.callback = function(n,m) {
		if (!lense.hasOwnProperty('callback')) {
			lense.callback = {};
		}
		lense.callback[n] = m;
	}
	
	/**
	 * Register Method
	 */
	this.method = function(n,m) {
		if (!lense.hasOwnProperty('method')) {
			lense.method = {};
		}
		lense.method[n] = m;
	}
});