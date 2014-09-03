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
		path: ['home', 'hosts', 'formula', 'admin']
	}, function() {
		c.push('api.CSAPIInterface');
	});

	// CloudScape: Login
	include({
		CSAuthInterface:    	   'app/auth/interface.js'
	}, {
		path: 'auth'
	}, function() {
		c.push('auth.CSAuthInterface');
	});

	// CloudScape: Home
	include({
		CSHomeInterface:    	   'app/home/interface.js'
	}, {
		path: 'home'
	}, function() {
		c.push('home.CSHomeInterface');
	});

	// CloudScape: Hosts
	include({
		CSHostsList:    	       'app/hosts/list.js',
		CSHostGroupsList:          'app/hosts/gplist.js',
		CSHostGroupEditor:		   'app/hosts/gpeditor.js',
		CSHostGroupDetails:        'app/hosts/gpdetails.js',
		CSHostDetails:      	   'app/hosts/details.js',
		CSHostsInterface:   	   'app/hosts/interface.js'
	}, {
		path: 'hosts'
	}, function() {
		c.push('hosts.CSHostsInterface');
	});
	
	// CloudScape: Formulas
	include({
		CSFormulaOverview:  	   'app/formula/overview.js',
		CSFormulaDetails:  		   'app/formula/details.js',
		CSFormulaRun:       	   'app/formula/run.js',
		CSFormulaInterface:        'app/formula/interface.js'
	}, {
		path: 'formula'
	}, function() {
		c.push('formula.CSFormulaInterface');
	});
	
	// CloudScape: Admin
	include({
		CSAdminACLList:            'app/admin/acllist.js',
		CSAdminACLDetails:         'app/admin/acldetails.js',
		CSAdminUsers:              'app/admin/users.js',
		CSAdminGroupsList:         'app/admin/gplist.js',
		CSAdminGroupDetails:       'app/admin/gpdetails.js',
		CSAdminInterface:          'app/admin/interface.js',
		CSAdminEndpointDetails:    'app/admin/epdetails.js',
		CSAdminEndpointList:       'app/admin/eplist.js',
		CSAdminACLObjectsList:     'app/admin/objlist.js',
		CSAdminACLObjectDetails:   'app/admin/objdetails.js',
		CSAdminDatacentersList:    'app/admin/dclist.js',
		CSAdminDatacentersDetails: 'app/admin/dcdetails.js'
	}, {
		path: 'admin'
	}, function() {
		c.push('admin.CSAdminInterface');
	});
	
	// Boostrap the constructors
	cs.bootstrap(c);
})();