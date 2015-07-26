(function() {
	
	// Class constructors
	var c = [];

	// CloudScape: Base
	include({
		CSBaseURL:          	   'base/url.js',
		CSBaseValidate:     	   'base/validate.js',
		CSBaseForms:        	   'base/forms.js',
		CSBaseLayout:       	   'base/layout.js',
		CSBaseButton:       	   'base/button.js',
		CSBaseRegister:     	   'base/register.js',
		CSBaseD3:           	   'base/d3.js',
		CSBaseInterface:    	   'base/interface.js',
		CSBaseIPAddr:              'base/ipaddr.js',
		CSBaseFinder:              'base/finder.js'
	}, null, function() {
		c.push('base.CSBaseInterface');
	});

	// CloudScape: API
	include({
		CSAPIClient:        	   'api/client.js',
		CSAPIRequest:       	   'api/request.js',
		CSAPIResponse:      	   'api/response.js',
		CSAPICache:         	   'api/cache.js',
		CSAPIInterface:     	   'api/interface.js'
	}, {
		url: {
			path: ['home', 'admin']
		}
	}, function() {
		c.push('api.CSAPIInterface');
	});

	// CloudScape: Login
	include({
		CSAuthInterface:    	   'app/auth/interface.js'
	}, {
		url: {
			path: 'auth'
		}
	}, function() {
		c.push('auth.CSAuthInterface');
	});

	// CloudScape: Home
	include({
		CSHomeInterface:    	   'app/home/interface.js'
	}, {
		url: {
			path: 'home'
		}
	}, function() {
		c.push('home.CSHomeInterface');
	});
	
	// CloudScape: Admin
	include({
		CSAdminACLList:            'app/admin/acl.list.js',
		CSAdminACLDetails:         'app/admin/acl.details.js',
		CSAdminUsers:              'app/admin/user.list.js',
		CSAdminGroupsList:         'app/admin/group.list.js',
		CSAdminGroupDetails:       'app/admin/group.details.js',
		CSAdminUtilityDetails:     'app/admin/utility.details.js',
		CSAdminUtilitiesList:      'app/admin/utility.list.js',
		CSAdminACLObjectsList:     'app/admin/object.list.js',
		CSAdminACLObjectDetails:   'app/admin/object.details.js',
		CSAdminInterface:          'app/admin/interface.js'
	}, {
		url: {
			path: 'admin'
		},
		is_admin: true
	}, function() {
		c.push('admin.CSAdminInterface');
	});
	
	// Boostrap the constructors
	cs.bootstrap(c);
})();