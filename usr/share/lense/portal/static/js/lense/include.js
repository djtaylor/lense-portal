(function() {
	
	// Class constructors
	var c = [];
	
	// Commons
	include({
		Common_URL: 'common/url.js',
		Common_Validate: 'common/validate.js',
		Common_Forms: 'common/forms.js',
		Common_Layout: 'common/layout.js',
		Common_Button: 'common/button.js',
		Common_Register: 'common/register.js',
		Common_Interface: 'common/interface.js',
		Common_IPAddr: 'common/ipaddr.js',
		Common_Finder: 'common/finder.js'
	}, null, function() {
		c.push('common.Common_Interface');
	});

	// API
	include({
		API_Client: 'api/client.js',
		API_Request: 'api/request.js',
		API_Response: 'api/response.js',
		API_Cache: 'api/cache.js',
		API_Interface: 'api/interface.js'
	}, {
		url: { path: ['home', 'admin'] }
	}, function() { 
		c.push('api.API_Interface'); 
	});
	
	// Authentication
	include({
		Auth_Interface: 'handlers/auth/interface.js'
	}, {
		url: { path: 'auth' }
	}, function() {
		c.push('auth.Auth_Interface');
	});
	
	// Home
	include({
		Home_Interface: 'handlers/home/interface.js'
	}, {
		url: { path: 'home' }
	}, function() {
		c.push('home.Home_Interface');
	});
	
	// Lense: Admin
	include({
		Admin_ACLKeyList: 'handlers/admin/acl.list.js',
		Admin_ACLKeyDetails: 'handlers/admin/acl.details.js',
		Admin_User: 'handlers/admin/user.list.js',
		Admin_GroupList: 'handlers/admin/group.list.js',
		Admin_GroupDetails: 'handlers/admin/group.details.js',
		Admin_HandlerDetails: 'handlers/admin/utility.details.js',
		Admin_HandlerList: 'handlers/admin/utility.list.js',
		Admin_ACLObjectList: 'handlers/admin/object.list.js',
		Admin_ACLObjectDetails: 'handlers/admin/object.details.js',
		Admin_Interface: 'handlers/admin/interface.js'
	}, {
		url: { path: 'admin' }, is_admin: true
	}, function() {
		c.push('admin.Admin_Interface');
	});
	
	// Boostrap the constructors
	lense.bootstrap(c);
})();