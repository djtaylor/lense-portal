lense.import('admin.users', function() {
	var self    = this;

	// Object definition
	this.object = lense.object.define('user');

	// Set object options
	this.object.setOptions({
		model: 'Users',
		handler: {
			get: 'user_get',
			update: 'user_update',
			delete: 'user_delete'
		}
	});

	// Define object template
	this.object.defineTemplate(new OrderedObject([
		[ 'username', {
			label: 'Username',
			link: true,
			edit: true,
			list: true
		}],
		[ 'first_name', {
			label: 'First Name',
			edit: true,
			list: true
		}],
		[ 'last_name', {
			label: 'Last Name',
			edit: true,
			list: true
		}],
		[ 'email', {
			label: 'Email',
			edit: true,
			list: true
		}],
		[ 'uuid', {
			label: 'UUID',
			def: '@lense.uuid4()',
			list: false
		}],
		[ 'from_ldap', {
			label: 'LDAP',
			type: 'bool',
			edit: false,
			def: false,
			list: true,
			map: {
				'Yes': true,
				'No': false
			}
		}]
	]));

	// User properties
	this.object.defineProperties('content-center', {
		exclude: ['date_joined']
	});

	// User's groups
	this.object.defineGroup('content-right', {
		members: 'groups',
		title: 'Groups',
		map: 'uuid',
		available: 'data.groups',
		fields: ['name', 'desc']
	});

	/**
	 * @constructor
	 */
	lense.register.constructor('admin.users', function() {

		// Bootstrap object
		self.object.bootstrap({
			data: {
				groups: 'group_get'
			}
		});
	});
});
