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

	// Lense: API Manager
	include({
		LenseAPIMInterface:        'app/apim/interface.js',
		LenseAPIMConnectorList:    'app/apim/connector.list.js',
		LenseAPIMConnectorDetails: 'app/apim/connector.details.js'
	}, {
		url: {
			path: 'apim'
		}
	}, function() {
		c.push('apim.LenseAPIMInterface');
	});
	
	// Lense: Login
	include({
		LenseAuthInterface:    	   'app/auth/interface.js'
	}, {
		url: {
			path: 'auth'
		}
	}, function() {
		c.push('auth.LenseAuthInterface');
	});

	// Lense: Home
	include({
		LenseHomeInterface:    	   'app/home/interface.js'
	}, {
		url: {
			path: 'home'
		}
	}, function() {
		c.push('home.LenseHomeInterface');
	});
	
	// Lense: Admin
	include({
		LenseAdminACLList:            'app/admin/acl.list.js',
		LenseAdminACLDetails:         'app/admin/acl.details.js',
		LenseAdminUsers:              'app/admin/user.list.js',
		LenseAdminGroupsList:         'app/admin/group.list.js',
		LenseAdminGroupDetails:       'app/admin/group.details.js',
		LenseAdminUtilityDetails:     'app/admin/utility.details.js',
		LenseAdminUtilitiesList:      'app/admin/utility.list.js',
		LenseAdminACLObjectsList:     'app/admin/object.list.js',
		LenseAdminACLObjectDetails:   'app/admin/object.details.js',
		LenseAdminInterface:          'app/admin/interface.js'
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