lense.import('admin.interface', function() {
	
	/**
	 * Initialize AdminInterface
	 * @constructor
	 */
	this.__init__ = function() {
	
		// Load modules
		lense.implement([
			['admin.users',    { view: 'users' }],
			['admin.groups',   { view: 'groups' }],
			['admin.handlers', { view: 'handlers' }],
			['admin.models',   { view: 'models' }]
		]);
	}
});