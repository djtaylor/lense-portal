lense.import('LenseAPIMInterface', function() {
	
	/**
	 * Initialize LenseAPIMInterface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// ACL management
		if (defined(lense.url.param_get('connector'))) {
			lense.implement('LenseAPIMConnectorDetails', 'apim.connector');
		} else {
			if (lense.url.param_get('panel') == 'connectors') {
				lense.implement('LenseAPIMConnectorList', 'apim.connector');
			}
		}
		
		// Document ready
		$(document).ready(function() {
			
		});
	}
});