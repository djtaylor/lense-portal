cs.import('CSNetworkRouterDetails', function() { 
	
	// Active router
	this.active = cs.url.param_get('router');
	
	/**
	 * Initialize: CSNetworkRouterDetails
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			$('.table_50').animate({
				opacity: '1.0'
			}, 500);
		});
	}
	
	/**
	 * Callback: Save Router
	 */
	cs.register.callback('router.save', function(c,m,d,a) {
		
	});
	
	/**
	 * Callback: Remove Interface
	 */
	cs.register.callback('router.remove_interface', function(c,m,d,a) {
		if (c == 200) {
			
		}
	});
	
	/**
	 * Callback: Add Interface
	 */
	cs.register.callback('router.add_interface', function(c,m,d,a) {
		if (c == 200) {
			
		}
	});
	
	/**
	 * Method: Save Router
	 */
	cs.register.method('router.save', function() {
		cs.layout.loading(true, 'Updating router...', function() {
			cs.api.request.post({
				path: 'network/router',
				action: 'update',
				_data: (function() {
					// Generate request data
				})(),
				callback: {
					id: 'router.save'
				}
			});
		});
	});
	
	/**
	 * Method: Edit Router
	 */
	cs.register.method('router.edit', function() {
		
	});
	
	/**
	 * Method: Remove Interface
	 */
	cs.register.method('router.remove_interface', function() {
		cs.layout.popup_toggle(false, 'router.remove_interface', false, function() { 
			cs.layout.loading(true, 'Removing router interface...', function() {
				cs.api.request.post({
					path: 'network/router/interface',
					action: 'remove',
					_data: (function() {
						// Generate request data
					})(),
					callback: {
						id: 'router.remove_interface'
					}
				});
			});
		});
	});
	
	/**
	 * Method: Add Interface
	 */
	cs.register.method('router.add_interface', function() {
		cs.layout.popup_toggle(false, 'router.add_interface', false, function() { 
			cs.layout.loading(true, 'Adding router interface...', function() {
				cs.api.request.post({
					path: 'network/router/interface',
					action: 'add',
					_data: (function() {
						// Generate request data
					})(),
					callback: {
						id: 'router.add_interface'
					}
				});
			});
		});
	});
});