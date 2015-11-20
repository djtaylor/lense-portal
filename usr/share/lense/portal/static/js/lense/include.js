(function() {
	
	// Class constructors
	var c = [];

	// Lense: Base
	include({
		LenseBaseURL:          	   'base/url.js',
		LenseBaseValidate:     	   'base/validate.js',
		LenseBaseForms:        	   'base/forms.js',
		LenseBaseLayout:       	   'base/layout.js',
		LenseBaseButton:       	   'base/button.js',
		LenseBaseRegister:     	   'base/register.js',
		LenseBaseInterface:    	   'base/interface.js',
		LenseBaseIPAddr:           'base/ipaddr.js',
		LenseBaseFinder:           'base/finder.js'
	}, null, function() {
		c.push('base.LenseBaseInterface');
	});

	// Lense: API
	include({
		LenseAPIClient:        	   'api/client.js',
		LenseAPIRequest:       	   'api/request.js',
		LenseAPIResponse:      	   'api/response.js',
		LenseAPICache:         	   'api/cache.js',
		LenseAPIInterface:     	   'api/interface.js'
	}, {
		url: {
			path: ['home', 'admin']
		}
	}, function() {
		c.push('api.LenseAPIInterface');
	});
	
	// Lense: Login
	include({
		LenseAuthInterface:    	   'handlers/auth/interface.js'
	}, {
		url: {
			path: 'auth'
		}
	}, function() {
		c.push('auth.LenseAuthInterface');
	});

	// Lense: Home
	include({
		LenseHomeInterface:    	   'handlers/home/interface.js'
	}, {
		url: {
			path: 'home'
		}
	}, function() {
		c.push('home.LenseHomeInterface');
	});
	
	// Lense: Admin
	include({
		LenseAdminACLList:            'handlers/admin/acl.list.js',
		LenseAdminACLDetails:         'handlers/admin/acl.details.js',
		LenseAdminUsers:              'handlers/admin/user.list.js',
		LenseAdminGroupsList:         'handlers/admin/group.list.js',
		LenseAdminGroupDetails:       'handlers/admin/group.details.js',
		LenseAdminUtilityDetails:     'handlers/admin/utility.details.js',
		LenseAdminUtilitiesList:      'handlers/admin/utility.list.js',
		LenseAdminACLObjectsList:     'handlers/admin/object.list.js',
		LenseAdminACLObjectDetails:   'handlers/admin/object.details.js',
		LenseAdminInterface:          'handlers/admin/interface.js'
	}, {
		url: {
			path: 'admin'
		},
		is_admin: true
	}, function() {
		c.push('admin.LenseAdminInterface');
	});
	
	// Boostrap the constructors
	lense.bootstrap(c);
})();