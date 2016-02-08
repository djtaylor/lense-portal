lense.import('LenseAdminGroupsList', function() {
	
	/**
	 * Callback: Create Group
	 */
	lense.register.callback('group.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][target="groups"]').append(lense.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type:   'row',
					target: 'groups',
					group:  d.uuid
				},
				children: [
				    lense.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [lense.layout.create.element('input', {
				    		attr: {
				    			type:   'radio',
				    			name:   'select_group',
				    			value:  d.uuid,
				    			action: 'update'
				    		}
				    	})]
				    }),
				    lense.layout.create.element('div', {
				    	css:  'table_col table_link',
				    	attr: {
				    		col:    'group_name',
				    		type:   'button',
				    		action: 'link',
				    		target: 'admin?panel=groups&group=' + d.uuid
				    	},
				    	text: d.name
				    }),
				    lense.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'group_desc'
				    	},
				    	text: d.desc
				    }),
				    lense.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'group_protected'
				    	},
				    	text: (d['protected']) ? 'Yes' : 'No'
				    })
				]
			}));
		}
		
		// Refresh the layout
		lense.layout.refresh();
	});
	
	/**
	 * Method: Create Group
	 */
	lense.register.method('group.create', function() {
		
		// Load the request data
		data = {};
		$('input[type="text"][form="create_group"]').each(function(i,o) {
			var a = get_attr(o);
			data[a.name] = $(o).val();
		});
		
		// Load the protected flag
		data['protected'] = ($('select[form="create_group"][name="protected"]').val() === 'true') ? true : false;
		
		// Submit the API request
		lense.layout.popup_toggle(false, 'group.create', false, function() { 
			lense.layout.loading(true, 'Creating API user group...', function() { 
				lense.api.request.post({
					path:   'group',
					_data:  data,
					callback: {
						id: 'group.create'
					}
				});
			});
		});
	});
	
	/**
	 * Callback: Delete Group
	 */
	lense.register.callback('group.delete', function(c,m,d,a) {
		if (c == 200) {
			$('input[type="hidden"][name="select_group"]').val('');
			lense.layout.remove('div[target="groups"][group="' + d.uuid + '"]');
		}
	});
	
	/**
	 * Method: Delete Group
	 */
	lense.register.method('group.delete', function() {
		var group = $('input[type="hidden"][name="select_group"]').val();
		if (defined(group)) {
			lense.layout.popup_toggle(false, 'group.delete', false, function() { 
				lense.layout.loading(true, 'Deleting API user group...', function() { 
					lense.api.request.del({
						path:   'group',
						_data:  {
							uuid:  group
						},
						callback: {
							id: 'group.delete'
						}
					});
				});
			});
		}
	});
});