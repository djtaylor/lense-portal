cs.import('CSAdminGroupsList', function() {
	
	/**
	 * Callback: Create Group
	 */
	cs.register.callback('group.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][target="groups"]').append(cs.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type:   'row',
					target: 'groups',
					group:  d.uuid
				},
				children: [
				    cs.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [cs.layout.create.element('input', {
				    		attr: {
				    			type:   'radio',
				    			name:   'select_group',
				    			value:  d.uuid,
				    			action: 'update'
				    		}
				    	})]
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col table_link',
				    	attr: {
				    		col:    'group_name',
				    		type:   'button',
				    		action: 'link',
				    		target: 'admin?panel=groups&group=' + d.uuid
				    	},
				    	text: d.name
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col: 'group_desc'
				    	},
				    	text: d.desc
				    }),
				    cs.layout.create.element('div', {
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
		cs.layout.refresh();
	});
	
	/**
	 * Method: Create Group
	 */
	cs.register.method('group.create', function() {
		
		// Load the request data
		data = {};
		$('input[type="text"][form="create_group"]').each(function(i,o) {
			var a = get_attr(o);
			data[a.name] = $(o).val();
		});
		
		// Load the protected flag
		data['protected'] = ($('select[form="create_group"][name="protected"]').val() === 'true') ? true : false;
		
		// Submit the API request
		cs.layout.popup_toggle(false, 'group.create', false, function() { 
			cs.layout.loading(true, 'Creating API user group...', function() { 
				cs.api.request.post({
					path:   'group',
					action: 'create',
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
	cs.register.callback('group.delete', function(c,m,d,a) {
		if (c == 200) {
			$('input[type="hidden"][name="select_group"]').val('');
			cs.layout.remove('div[target="groups"][group="' + d.uuid + '"]');
		}
	});
	
	/**
	 * Method: Delete Group
	 */
	cs.register.method('group.delete', function() {
		var group = $('input[type="hidden"][name="select_group"]').val();
		if (defined(group)) {
			cs.layout.popup_toggle(false, 'group.delete', false, function() { 
				cs.layout.loading(true, 'Deleting API user group...', function() { 
					cs.api.request.post({
						path:   'group',
						action: 'delete',
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