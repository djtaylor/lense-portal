lense.import('admin.handlers', function() {
	var self    = this;

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
			list: true
		}],
		[ 'desc', {
			label: 'Description',
			edit: true,
			list: false
		}],
		[ 'uuid', {
			label: 'UUID',
			def: '@lense.uuid4()',
			list: false
		}],
		[ 'path', {
			label: 'Path',
			edit: true,
			list: true
		}],
		[ 'method', {
			label: 'Method',
			type: 'select',
			options: ['GET', 'PUT', 'POST', 'DELETE'],
			edit: true,
			list: true
		}],
		[ 'enabled', {
			label: 'Enabled',
			type: 'bool',
			edit: true,
			def: true,
			list: true,
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
			list: true,
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
			list: true,
			map: {
				'Yes': true,
				'No': false
			}
		}],
		[ 'locked_by', {
			label: 'Locked By',
			list: false
		}],
		[ 'allow_anon', {
			label: 'Anonymous',
			edit: true,
			type: 'bool',
			map: {
				'Yes': true,
				'No': false
			}
		}],
		[ 'manifest', {
			def: []
		}]
	]));

	// Object grid center
	this.object.defineGrid('content-center', {
		key: 'manifest',
		require: [
			'HandlerVariable',
			'HandlerAction',
			'HandlerParameters',
			'HandlerResponse'
		]
	});

	// Object properties right
	this.object.defineProperties('content-right', {
		exclude: ['manifest', 'locked_by']
	});

	/**
	 * @constructor
	 */
	lense.register.constructor('admin.models', function() {

		// Bootstrap object
		self.object.bootstrap();
	});
});
