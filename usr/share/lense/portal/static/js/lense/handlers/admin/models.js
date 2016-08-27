lense.import('admin.models', function() {
	var self = this;

	// Object definition
	this.object = lense.object.define('handler', url.param_get('uuid', false), {
		model: 'Handlers',
		grid: 'manifest',
		handler: {
			get: 'handler_get',
			update: 'handler_update',
			delete: 'handler_delete'
		}
	});

	/**
	 * @constructor
	 */
	lense.register.constructor('admin.models', function() {

		// Load required object types
		self.object.require([
			'HandlerVariable',
			'HandlerAction',
			'HandlerParameters',
			'HandlerResponse'
		]);

		// Register object list constructor method
		self.object.constructList(function(data) {

			// List object properties
			var properties = [
				{
					name: {
						label: 'Name',
						link: true
					}
				},
				{
					path: {
						label: 'Path'
					}
				},
				{
					method: {
						label: 'Method'
					}
				},
				{
					enabled: {
						label: 'Enabled',
						map: {
							'Yes': true,
							'No': false
						}
					}
				},
				{
					protected: {
						label: 'Protected',
						map: {
							'Yes': true,
							'No': false
						}
					}
				},
				{
					locked: {
						label: 'Locked',
						map: {
							'Yes': true,
							'No': null
						}
					}
				}
			];

			// Object header
			self.object.render('header');

			// List controls
			self.object.render('list-controls')(properties);

			// List objects (rows)
			self.object.render('rows-body')(self.object.defineRows(data, properties));

			// List objects (thumbnails)
			self.object.render('list-thumbnails')(self.object.defineThumbnails(data, properties, {
				title: 'name'
			}));
		});

		// Register single object constructor method
		self.object.constructObject(function(data) {

			// Object source data
			self.object.setData(data, {
				filter: ['id']
			});

			// Object header
			self.object.render('header');

			// Handler manifest
			self.object.renderGrid('content-center')('manifest', data, {
				extract: 'manifest'
			});

			// Handler properties
			self.object.render('content-right')(self.object.defineProperties(data, {
				name: {
					edit: true
				},
				uuid: {
					label: 'UUID'
				},
				desc: {
					edit: true,
					label: 'Description'
				},
				path: {
					edit: true
				},
				method: {
					type: 'select',
					options: ['GET', 'PUT', 'POST', 'DELETE'],
					edit: true
				},
				enabled: {
					type: 'bool',
					edit: true
				},
				protected: {
					type: 'bool',
					edit: true
				},
				allow_anon: {
					type: 'bool',
					label: 'Anonymous Requests',
					edit: true
				},
				locked: {
					type: 'bool',
					edit: true
				},
				locked_by: {
					type: 'str',
					label: 'Locked By'
				}
			}));
		});

		// Bootstrap object
		self.object.bootstrap();
	});
});
