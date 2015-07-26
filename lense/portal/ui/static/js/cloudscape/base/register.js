/**
 * CloudScape Method Registration
 */
cs.import('CSBaseRegister', function() {
	
	/**
	 * Register Callback
	 */
	this.callback = function(n,m) {
		if (!cs.hasOwnProperty('callback')) {
			cs.callback = {};
		}
		cs.callback[n] = m;
	}
	
	/**
	 * Register Method
	 */
	this.method = function(n,m) {
		if (!cs.hasOwnProperty('method')) {
			cs.method = {};
		}
		cs.method[n] = m;
	}
});