lense.import('Admin_Interface', function() {
	
	/**
	 * Initialize LenseAdminInterface
	 * @constructor
	 */
	this.__init__ = function() {
	
		// ACL management
		if (defined(lense.url.param_get('acl'))) {
			lense.implement('Admin_ACLKeyDetails', 'admin.acl');
		} else {
			if (lense.url.param_get('panel') == 'acls') {
				lense.implement('Admin_ACLKeyList', 'admin.acl');
			}
		}
		
		// Admin Users
		if (lense.url.param_get('panel') == 'users') {
			lense.implement('Admin_User', 'admin.users');
		}
		
		// Group Details
		if (defined(lense.url.param_get('group'))) {
			lense.implement('Admin_GroupDetails', 'admin.groups');
		
		// Group List
		} else {
			if (lense.url.param_get('panel') == 'groups') {
				lense.implement('Admin_GroupList', 'admin.groups');
			}
		}
		
		// Utility Details
		if (defined(lense.url.param_get('utility'))) {
			lense.implement('Admin_HandlerDetails', 'admin.utility')
		
		// Utilities List
		} else {
			if (lense.url.param_get('panel') == 'utilities') {
				lense.implement('Admin_HandlerList', 'admin.utility');
			}
		}
		
		// ACL Objects Details
		if (defined(lense.url.param_get('object'))) {
			lense.implement('Admin_ACLObjectDetails', 'admin.acl_objects');
		
		// ACL Objects List
		} else {
			if (lense.url.param_get('panel') == 'objects') {
				lense.implement('Admin_ACLObjectList', 'admin.acl_objects');
			}
		}
	}
	
	/**
	 * Construct Inactive Text Field
	 * 
	 * Helper method to construct inactive text fields in dynamically generated forms.
	 * 
	 * @param {f} The parent form
	 * @param {n} The field name
	 * @param {v} The field value
	 */
	this.input_inactive = function(f,n,v) {
		return lense.layout.html(
			$('<input/>').attr({
				'type':     'text',
				'form':     f,
				'name':     n,
				'readonly': 'yes',
				'value':    v,
				'noreset':  ''
			})
		);
	}
	
	/**
	 * Construct Input Dropdown
	 */
	this.input_dropdown = function(p) {
		
		// Bind the onchange event
		$(document).on('change', 'select[form$="' + p.form + '"][name$="' + p.name + '"]', function(e) {
			$('input[type$="hidden"][form$="' + p.form + '"][name$="' + p.name + '"]').val($(this).find(':selected').attr('value'));
		});
		
		// Construct and return the dropdown element
		return lense.layout.create.element('div', {
			children: [
			    lense.layout.create.element('select', {
			    	css:  'table_col_select_dropdown',
			    	attr: (function() {
			    		var b = {
			    			name: p.name,
			    			form: p.form
			    		};
			    		if (p.hasOwnProperty('disabled') && p.disabled === true) {
			    			b.disabled = '';
			    		}
			    		return b;
			    	})(),
			    	children: (function() {
			    		var c = [];
			    		$.each(p.options, function(k,v) {
			    			c.push(lense.layout.create.element('option', {
			    				attr: (function() {
			    					var a = { value: v };
			    					if (k == p.selected) {
			    						a.selected = 'selected';
			    					}
			    					return a;
			    				})(),
			    				text: k
			    			}));
			    		});
			    		return c;
			    	})()
			    }),
			    lense.forms.create.input_hidden({
					form:    p.form,
					name:    p.name,
					value:   p.options[p.selected],
					noreset: ''
				})
			]
		});
	}
	
	/**
	 * Construct Object Profile
	 * 
	 * Method used to construct the profile section for the user or group object. The profile
	 * section contains details such as user/group name and description.
	 * 
	 * @param {p} Object profile parameters
	 */
	this.obj_profile = function(p) {
		return lense.layout.create.table.panel({
			name:    p.table.name,
			title:   'Profile',
			rows:    (function() {
				var r = [];
				$.each(p.source.keys, function(k,l) {
					r.push(lense.layout.create.element('div', {
						css: 'table_row',
						children: [
						    lense.layout.create.element('div', {
						    	css:  'table_row_label',
						    	text: l
						    }),
						    lense.layout.create.element('div', {
						    	css: 'table_row_input',
						    	children: [lense.admin.input_inactive(p.table.form,'profile/' + k, p.source.object[k])]
						    })
						]
					}));
				});
				return r;
			})()
		});
	}
	
	/**
	 * Construct Object Table
	 * 
	 * @param {p} Parameters object
	 */
	this.obj_table = function(p) {
		
		// Table rows
		tr = [];
		
		// Construction flags
		var construct = {
			select:  (p.source.hasOwnProperty('select')) ? p.source.select : false,
			headers: (p.source.hasOwnProperty('headers')) ? p.source.headers : false,
			rows:    (p.source.hasOwnProperty('rows')) ? p.source.rows : false
		};
		
		// If creating column headers
		if (construct.headers) {
			tr.push(lense.layout.create.table.headers({
				select:   construct.select,
				keys:     p.source.keys,
				size:     'md',
				minwidth: '150'
			}));
		}
		
		// Construct the table rows
		if (construct.rows) {
			$.each(p.source.object, function(i,o) {
				r = $('<div></div>').addClass('table_row').attr({
					type: 'row',
					target: p.table.name
				});
				if (p.table.key[1] instanceof Array) {
					r.attr(p.table.key[1][0], o[p.table.key[1][1]]);
				} else {
					r.attr(p.table.key[1], o[p.table.key[1]]);
				}
				
				// If inserting a select column
				if (construct.select) {
					r.append(lense.layout.create.element('div', {
						css: 'table_select_col',
						children: [lense.layout.create.element('input', {
							attr: (function() {
								var b = {
									type:     'radio',
									name:     p.table.key[0],
									value:    (function() {
										return (p.table.key[1] instanceof Array) ? o[p.table.key[1][1]]: o[p.table.key[1]];
									})(),
									action:   'update',
									ignore:   '',
									disabled: '',
									form:     'edit_group',
									noreset:  ''
								};
								if (construct.select.hasOwnProperty('attr')) {
									$.each(construct.select.attr, function(k,v) {
										b[k] = v;
									});
								}
								return b;
							})()
						})]
					}));
				}
				
				// Scan the source keys
				$.each(p.source.keys, function(k,l) {
					c = $('<div></div>').addClass('table_col').attr({
						'col': k,
						'mw': '150'
					});
					
					// If creating a dynamic input field
					if (p.table.hasOwnProperty('fields') && (k in p.table.fields)) {
							
						// Select menu
						if (p.table.fields[k].type == 'select') {
							c.append(lense.admin.input_dropdown({
								form: p.table.form,
								name: (function() {
									return (p.table.key[1] instanceof Array) ? p.table.param_base + '/' + o[p.table.key[1][1]]: o[p.table.key[1]];
								})(),
								options: p.table.fields[k].options,
								selected: o[k],
								disabled: true
							}));
						}
					} else {
						c.text(o[k]);
					}
					r.append(lense.layout.html(c));
				});
				tr.push(lense.layout.html(r));
			});
		}
		
		// Construct the table panel
		return lense.layout.create.table.panel({
			name:    p.table.name,
			title:   p.table.title,
			actions: p.table.actions,
			rows:    tr
		});
	}
});