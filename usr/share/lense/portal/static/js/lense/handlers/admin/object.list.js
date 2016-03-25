lense.import('Admin_ACLObjectList', function() { 
	
	/**
	 * Initialize LenseAdminACLObjectsList
	 * @constructor
	 */
	this.__init__ = function() {}
	
	/**
	 * Callback: Create Object
	 */
	lense.register.callback('acl.create_object', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][target="acl_objects"]').append(lense.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type: 'row',
					target: 'acl_object',
					acl_object: d.type
				},
				children: [
				    lense.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [lense.layout.create.element('input', {
				    		attr: {
				    			type:   'radio',
				    			name:   'select_object',
				    			action: 'update'
				    		}
				    	})]
				    }),
				    lense.layout.create.element('div', {
				    	css:  'table_col table_link',
				    	attr: {
				    		col:    'ao_type',
				    		type:   'button',
				    		action: 'method',
				    		target: 'acl.toggle_object',
				    		arg:    d.type
				    	},
				    	text: d.type
				    }),
				    lense.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'ao_name'
				    	},
				    	text: d.name
				    }),
				    lense.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'ao_count'
				    	},
				    	text: '0'
				    })
				]
			}));
			
			// Refresh the layout
			lense.layout.refresh();
		}
	});
	
	/**
	 * Method: Create Object
	 */
	lense.register.method('acl.create_object', function() {
		
		// Request data
		data = {};
		
		// Construct the string attributes
		$('input[type="text"][form="create_acl_object"]').each(function(i,e) {
			var a = get_attr(e);
			data[a.name] = $(e).val();
		});
		
		// Get the default ACL definition
		def_acl = $('select[form="create_acl_object"][name="def_acl"]').find(':selected').val();
		if (defined(def_acl)) {
			data['def_acl'] = def_acl;
		}
		
		// Submit the API request
		lense.layout.popup_toggle(false, 'acl.create_object', false, function() {
			lense.api.request.post({
				path:     'acl/objects',
				callback: {
					id: 'acl.create_object'
				},
				_data: data
			});
		});
	});
	
	/**
	 * Callback: Delete Object
	 */
	lense.register.callback('acl.delete_object', function(c,m,d,a) {
		if (c == 200) {
			
			// Reset the hidden input
			$('input[type="hidden"][name="select_object"]').val('');
			
			// Remove the ACL object row
			lense.layout.remove('div[type="row"][target="acl_object"][acl_object="' + d.type + '"]');
		}
	});
	
	/**
	 * Method: Delete Object
	 */
	lense.register.method('acl.delete_object', function() {
		
		// Get the selected object
		var s = $('input[type="hidden"][name="select_object"]').val();
		if (defined(s)) {
		
			// Submit the API request
			lense.layout.popup_toggle(false, 'acl.delete_object', false, function() {
				lense.api.request.del({
					path:     'acl/objects',
					callback: {
						id: 'acl.delete_object'
					},
					_data: {
						type: s
					}
				});
			});
		}
	});
});