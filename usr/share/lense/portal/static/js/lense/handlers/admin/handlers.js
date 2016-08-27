lense.import('admin.handlers', function() {
	var self = this;

	// Object definition
	this.object = lense.object.define('handler');

	// Set object options
	this.object.setOptions({
		model: 'Handlers',
		grid: 'manifest',
		handler: {
			get: 'handler_get',
			update: 'handler_update',
			delete: 'handler_delete'
		}
	});

	// Define object template
	this.object.defineTemplate(new OrderedObject([
		[ 'name', {
			label: 'Name',
			link: true,
			edit: true,
		}],
		[ 'desc', {
			label: 'Description',
			edit: true
		}],
		[ 'uuid', {
			label: 'UUID',
			def: '@lense.uuid4()',
			list: false
		}],
		[ 'path', {
			label: 'Path',
			edit: true
		}],
		[ 'method', {
			label: 'Method',
			type: 'select',
			options: ['GET', 'PUT', 'POST', 'DELETE'],
			edit: true
		}],
		[ 'enabled', {
			label: 'Enabled',
			type: 'bool',
			edit: true,
			def: true,
			map: {
				'Yes': true,
				'No': false
			}
		}],
		[ 'protected', {
			label: 'Protected',
			type: 'bool',
			edit: true,
			def: false,
			map: {
				'Yes': true,
				'No': false
			}
		}],
		[ 'locked', {
			label: 'Locked',
			type: 'bool',
			edit: true,
			create: false,
			list: false,
			map: {
				'Yes': true,
				'No': false
			}
		}],
		[ 'locked_by', {
			label: 'Locked By',
			list: false
		}],
		[ 'manifest': {
			grid: true,
			def: []
		}]
	]);

	// Object grid center
	this.object.defineGrid('center', {
		key: 'manifest',
		require: [
			'HandlerVariable',
			'HandlerAction',
			'HandlerParameters',
			'HandlerResponse'
		]
	});

	// Object properties right
	this.object.defineProperties('right', {
		exclude: ['manifest']
	}));

	/**
	 * @constructor
	 */
	lense.register.constructor('admin.models', function() {

		// Bootstrap object
		self.object.bootstrap();
	});
});
