lense.import('admin.groups', function() {
	var self    = this;

	// Object definition
	this.object = lense.object.define('group');

	// Set object options
	this.object.setOptions({
		model: 'Groups',
		handler: {
			get: 'group_get',
			update: 'group_update',
			delete: 'group_delete'
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
			list: true
		}],
		[ 'uuid', {
			label: 'UUID',
			def: '@lense.uuid4()',
			list: false
		}],
		[ 'protected', {
			label: 'Protected',
			type: 'bool',
			edit: false,
			def: false,
			list: true,
			map: {
				'Yes': true,
				'No': false
			}
		}],
		[ 'members', {
			label: 'Members',
			type: 'list'
		}]
	]));

	// Object properties center
	this.object.defineProperties('content-center', {
		exclude: ['members']
	});

	// Group members
	this.object.defineGroup('content-right', {
		members: 'members',
		map: 'uuid',
		available: 'data.users',
		fields: ['username', 'email']
	});

	/**
	 * @constructor
	 */
	lense.register.constructor('admin.groups', function() {
		self.object.bootstrap({
			data: {
				users: 'user_get'
			}
		});
	});
});
