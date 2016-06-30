lense.import('tools.interface', function() {
	
	/**
	 * Initialize LenseTools
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load modules
		lense.implement([
			['tools.manifests', { view: 'manifests' }]     
		]);
	}
});