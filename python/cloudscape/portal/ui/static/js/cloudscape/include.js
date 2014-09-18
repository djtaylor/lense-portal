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
			path: ['home', 'hosts', 'formula', 'admin', 'network']
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

	// CloudScape: Network
	include({
		CSNetworkRoutersList:      'app/network/router.list.js',
		CSNetworkRouterDetails:    'app/network/router.details.js',
		CSNetworkInterface:        'app/network/interface.js',
		CSNetworkIPBlocksList:     'app/network/ipblock.list.js',
		CSNetworkIPBlockDetails:   'app/network/ipblock.details.js'
	}, {
		url: {
			path: 'network'
		}
	}, function() {
		c.push('network.CSNetworkInterface');
	});
	
	// CloudScape: Hosts
	include({
		CSHostsList:    	       'app/hosts/host.list.js',
		SHostDetails:      	   	   'app/hosts/host.details.js',
		CSHostGroupsList:          'app/hosts/group.list.js',
		CSHostGroupEditor:		   'app/hosts/group.editor.js',
		CSHostGroupDetails:        'app/hosts/group.details.js',
		CSHostsInterface:   	   'app/hosts/interface.js'
	}, {
		url: {
			path: 'hosts'
		}
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
		url: {
			path: 'formula'
		}
	}, function() {
		c.push('formula.CSFormulaInterface');
	});
	
	// CloudScape: Admin
	include({
		CSAdminACLList:            'app/admin/acl.list.js',
		CSAdminACLDetails:         'app/admin/acl.details.js',
		CSAdminUsers:              'app/admin/user.list.js',
		CSAdminGroupsList:         'app/admin/group.list.js',
		CSAdminGroupDetails:       'app/admin/group.details.js',
		CSAdminEndpointDetails:    'app/admin/endpoint.details.js',
		CSAdminEndpointList:       'app/admin/endpoint.list.js',
		CSAdminACLObjectsList:     'app/admin/object.list.js',
		CSAdminACLObjectDetails:   'app/admin/object.details.js',
		CSAdminDatacentersList:    'app/admin/datacenter.list.js',
		CSAdminDatacentersDetails: 'app/admin/datacenter.details.js',
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
	try {
		cs.bootstrap(c);
	} catch (e) {
		console.log('Failed to bootstrap includes');
		console.log(e.stack);
	}
})();