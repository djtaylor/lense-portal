lense.import('Bootstrap_Interface', function() {
	
	/**
	 * Bootstrap session
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			$.each(['api_user', 'api_group', 'api_key', 'api_token'], function(i,k) {
				Cookies.set(k, lense.url.param_get(k));
			});
			
			// Redirect to home
			lense.url.redirect('home');
		});
	}
});