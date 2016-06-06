lense.import('common.interface', function() {
	var self = this;
	
	/**
	 * Initialize Interface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load modules
		lense.implement([
		    'common.url',
		    'common.forms',
		    'common.button',
		    'common.layout',
		    'common.validate',
		    'common.ipaddr',
		]);
		
		// Document ready
		$(document).ready(function() {
			
			// Parse the URL and load any rendered forms
			lense.common.url.parse();
		});
		
		// Bind actions
		self._bind();
	}
	
	/**
	 * Bind Global Actions
	 */
	this._bind = function() {
		
		// Click logout button
		$(document).on('click', '#form-logout-button', function() {
			$.each(lense.api.client.cookies, function(i,k) {
				Cookies.remove(k);
			});
			
			// Submit the logout form
			$('#form-logout').submit();
		});
	}
});