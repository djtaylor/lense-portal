/**
 * CloudScape Hosts Interface
 */
cs.import('CSHostsInterface', function() {
	
	/**
	 * Initialize CSHostsInterface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// List
		if (cs.url.param_get('panel') == 'list') {
			cs.implement('CSHostsList', 'hosts');
		}
		
		// Host Group Details
		if (defined(cs.url.param_get('group'))) {
			
			// Edit
			if (cs.url.param_exists('edit')) {
				cs.implement('CSHostGroupEditor', 'hosts');
				
			// Details
			} else {
				cs.implement('CSHostGroupDetails', 'hosts');
			}
			
		// Host Groups List
		} else {
			if (cs.url.param_get('panel') == 'groups') {
				cs.implement('CSHostGroupsList', 'hosts');
			}
		}
		
		// Details
		if (cs.url.param_get('panel') == 'details') {
			cs.implement('CSHostDetails', 'hosts');
		}
	}
});