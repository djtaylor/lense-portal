cs.import('CSNetworkInterface', function() {
	
	/**
	 * Initialize CSNetworkInterface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// IP Blocks
		if (defined(cs.url.param_get('block'))) {
			cs.implement('CSNetworkIPBlockDetails', 'network.ipblock');
			
		} else {
			if (cs.url.param_get('panel') == 'ipv4blocks' || cs.url.param_get('panel') == 'ipv6blocks') {
				cs.implement('CSNetworkIPBlockDetails', 'network.ipblock');
			}
		}
		
		// Routers
		if (defined(cs.url.param_get('router'))) {
			cs.implement('CSNetworkRouterDetails', 'network.router');
			
		} else {
			if (cs.url.param_get('panel') == 'routers') {
				cs.implement('CSNetworkRoutersList', 'network.router');
			}
		}
	}
});