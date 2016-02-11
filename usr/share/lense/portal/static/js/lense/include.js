(function() {
	
	// Class constructors
	var c = [];

	// User Interface
	include({
		UI: 'ui/common.js'
	}, null, function() {
		c.push('ui.Common');
	});
	
	// Commons
	include({
		URL: 'common/url.js',
		Validate: 'common/validate.js',
		Forms: 'common/forms.js',
		Layout: 'common/layout.js',
		Button: 'common/button.js',
		Register: 'common/register.js',
		Interface: 'common/interface.js',
		IPAddr: 'common/ipaddr.js',
		Finder: 'common/finder.js'
	}, null, function() {
		c.push('common.Interface');
	});

	// API
	include({
		Client: 'api/client.js',
		Request: 'api/request.js',
		Response: 'api/response.js',
		Cache: 'api/cache.js',
		Interface: 'api/interface.js'
	}, {
		url: { path: ['home', 'admin'] }
	}, function() { 
		c.push('api.Interface'); 
	});
	
	// Authentication
	include({
		Interface: 'handlers/auth/interface.js'
	}, {
		url: { path: 'auth' }
	}, function() {
		c.push('auth.Interface');
	});

	// Home
	include({
		Interface: 'handlers/home/interface.js'
	}, {
		url: { path: 'home' }
	}, function() {
		c.push('home.Interface');
	});
	
	// Lense: Admin
	include({
		ACLKeysList: 'handlers/admin/acl.list.js',
		ACLKeysDetails: 'handlers/admin/acl.details.js',
		Users: 'handlers/admin/user.list.js',
		GroupsList: 'handlers/admin/group.list.js',
		GroupDetails: 'handlers/admin/group.details.js',
		HandlerDetails: 'handlers/admin/utility.details.js',
		HandlerList: 'handlers/admin/utility.list.js',
		ACLObjectsList: 'handlers/admin/object.list.js',
		ACLObjectDetails: 'handlers/admin/object.details.js',
		Interface: 'handlers/admin/interface.js'
	}, {
		url: { path: 'admin' }, is_admin: true
	}, function() {
		c.push('admin.Interface');
	});
	
	// Boostrap the constructors
	lense.bootstrap(c);
})();