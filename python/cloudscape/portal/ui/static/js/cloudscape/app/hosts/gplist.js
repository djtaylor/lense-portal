cs.import('CSHostGroupsList', function() { 
	
	/**
	 * Callback: Delete Host Group
	 */
	cs.register.callback('hgroup.delete', function(c,m,d,a) {
		console.log(d);
		if (c == 200) {
			cs.layout.remove('div[type="row"][hgroup="' + d.uuid + '"]');
		}
	});
	
	/**
	 * Method: Delete Host Group
	 */
	cs.register.method('hgroup.delete', function(){ 
		var h = $('input[type="hidden"][name="hgroup_uuid"]').val();
		if (defined(h)) {
			cs.layout.popup_toggle(false, 'hgroup.delete', false, function() {
				cs.api.request.post({
					path: 'host/group',
					action: 'delete',
					_data: {
						uuid: h
					},
					callback: {
						id: 'hgroup.delete'
					}
				});
			});
		}
	});
	
	/**
	 * Callback: Create Host Group
	 */
	cs.register.callback('hgroup.create', function(c,m,d,a) {
		if (c == 200) {
			
			// Construct the new host group row
			$('div[type="rows"][target="hgroups"]').append(cs.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type:   'row',
					target: 'hgroups',
					hgroup: d.uuid
				},
				children: [
				    cs.layout.create.element('div', {
				    	css: 'table_select_col',
				    	children: [cs.layout.create.element('input', {
				    		attr: {
				    			type:   'radio',
				    			name:   'hgroup_uuid',
				    			value:  d.uuid,
				    			action: 'update'
				    		}
				    	})]
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col:    'hgroup_name',
				    		type:   'button',
				    		action: 'link',
				    		target: 'hosts?panel=groups&group=' + d.uuid
				    	},
				    	text: d.name
				    }),
				    cs.layout.create.element('div', {
				    	css:  'table_col',
				    	attr: {
				    		col:    'hgroup_uuid'
				    	},
				    	text: d.uuid,
				    }),
				    (function() {
				    	if (d.formula) {
				    		return cs.layout.create.element('div', {
				    			css:  'table_col table_link',
				    			attr: {
				    				col:   'hgroup_formula',
				    				type:   'button',
				    				action: 'link',
				    				target: 'formula?panel=details&formula=' + d.formula
				    			},
				    			text: d.formula
				    		});
				    	} else {
				    		return cs.layout.create.element('div', {
				    			css:  'table_col',
				    			attr: {
				    				col: 'hgroup_formula',
				    			},
				    			text: ''
				    		});
				    	}
				    })()
				]
			}));
			
			// Refresh the layout
			cs.layout.refresh();
		}
	});
	
	/**
	 * Method: Create Host Group
	 */
	cs.register.method('hgroup.create', function() {
		var n = $('input[form="hgroup_create"][name="name"]').val();
		
		// Submit the API request
		cs.layout.popup_toggle(false, 'hgroup.create', false, function() {
			cs.api.request.post({
				path: 'host/group',
				action: 'create',
				_data: {
					name:  n
				},
				callback: {
					id: 'hgroup.create'
				}
			});
		});
	});
});