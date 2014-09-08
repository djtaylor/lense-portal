cs.import('CSAdminDatacentersList', function() {
	
	/**
	 * Initialize CSAdminDatacentersList
	 * @constructor
	 */
	this.__init__ = function() {}
	
	/**
	 * Callback: Delete Datacenter
	 */
	cs.register.callback('datacenter.delete', function(c,m,d,a) {
		if (c == 200) {
			cs.layout.remove('div[type="row"][target="datacenter"][datacenter="' + d.uuid + '"]');
		}
	});
	
	/**
	 * Callback: Create Datacenter
	 */
	cs.register.callback('datacenter.create', function(c,m,d,a) {
		if (c == 200) {
			
			// Create the new datacenter row
			$('div[type="rows"][target="datacenters"]').append(cs.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type:       'row',
					target:     'datacenter',
					datacenter: d.uuid
				},
				children: [
				    cs.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [cs.layout.create.element('input', {
				    		attr: {
				    			type:   'radio',
				    			name:   'datacenter_uuid',
				    			value:  d.uuid,
				    			action: 'update'
				    		}
				    	})]
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col table_link',
				    	attr: {
				    		type:   'button',
				    		action: 'link',
				    		target: 'admin?panel=datacenters&datacenter=' + d.uuid,
				    		col:    'datacenter_name'
				    	},
				    	text: d.name
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'datacenter_label'
				    	},
				    	text: d.label
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'datacenter_uuid'
				    	},
				    	text: d.uuid
				    })
				]
			}));
			
			// Refresh the layout
			cs.layout.refresh();
		}
	});
	
	/**
	 * Method: Delete Datacenter
	 */
	cs.register.method('datacenter.delete', function() {
		var d = $('input[type="hidden"][name="datacenter_uuid"]').val();
		if (defined(d)) {
			cs.layout.popup_toggle(false, 'datacenter.delete', false, function() { 
				cs.layout.loading(true, 'Deleting datacenter...', function() {
					cs.api.request.post({
						path: 'locations/datacenters',
						action: 'delete',
						_data: {
							uuid: d
						},
						callback: {
							id: 'datacenter.delete'
						}
					});
				});
			});
		}
	});
	
	/**
	 * Method: Create Datacenter
	 */
	cs.register.method('datacenter.create', function() {
		var params = {};
		
		// Load the request parameters
		$.each($('input[form="datacenter_create"]'), function(i,e) {
			params[$(e).attr('name')] = $(e).val();
		});
		
		// Submit the API request
		cs.layout.popup_toggle(false, 'datacenter.create', false, function() { 
			cs.layout.loading(true, 'Creating datacenter...', function() {
				cs.api.request.post({
					path: 'locations/datacenters',
					action: 'create',
					_data: {
						name:  params.name,
						label: params.label
					},
					callback: {
						id: 'datacenter.create'
					}
				});
			});
		});
	});
});