cs.import('CSAdminEndpointList', function() {
	
	/**
	 * Initialize CSAdminEndpointList
	 * @constructor
	 */
	this.__init__ = function() {

		// Document ready
		$(document).ready(function() {
			cs.admin.endpoint.bind();
			cs.admin.endpoint.layout();
		});
		
		// Window resize
		$(window).resize(function() {
			cs.admin.endpoint.layout();
		});
	}
	
	/**
	 * Set Page Layout
	 */
	this.layout = function() {
		
		// Height attributes
		var height = {
			table: 		  $('#endpoint_list_table').actual('outerHeight', {includeMargin: true}),
			title:		  $('#endpoint_list_title').actual('outerHeight', {includeMargin: true}),
			header_title: $('div[class="table_headers"][table="endpoint_list"]').actual('outerHeight', {includeMargin: true})
		}
		
		// Define the height of the rows container
		var rows_height = (height.table - (height.title + height.header_title + 10));
		
		// Set the height of rows container
		$('div[type="rows"][table="endpoint_list"]').height(rows_height + 'px').css('overflow', 'auto');
	}
	
	/**
	 * Bind Form Events
	 */
	this.bind = function() {
			
		// Changes to new module input
		$('input[type="text"][name="mod_new"]').on('input', function() {
			
			// Update the hidden input
			cs.forms.set_field('input[type="hidden"][name="mod"]', $(this).val());
		});
		
		// Changes to the method input
		$('select[name="ep_method"][form="create_endpoint"]').on('change', function() {
			var s = $(this).find('option:selected');
			cs.forms.set_field('input[type="hidden"][name="ep_method"]', $(s).val());
		});
		
		// Changes to the enabled input
		$('select[name="enabled"][form="create_endpoint"]').on('change', function() {
			var s = $(this).find('option:selected');
			cs.forms.set_field('input[type="hidden"][name="enabled"]', $(s).val());
		});
		
		// Changes to the protected input
		$('select[name="protected"][form="create_endpoint"]').on('change', function() {
			var s = $(this).find('option:selected');
			cs.forms.set_field('input[type="hidden"][name="protected"]', $(s).val());
		});
		
		// Changes to the external utilities input
		$('select[name="utils"][form="create_endpoint"]').on('change', function() {
			var u = [];
			$($(this).find('option:selected')).each(function(i,o) {
				if (defined($(o).val())) {
					u.push($(o).val());
				}
			});
			cs.forms.set_field('input[type="hidden"][name="utils"]', u.join(','));
		});
		
		// Select a module
		$('select[name="mod"][form="create_endpoint"]').on('change', function() {
			var s = $(this).find('option:selected');
			
			// Custom module
			if ($(s).val() == 'new') {
				
				// Show the custom module text input
				$('div[target="popup_new"]').fadeIn('fast', function() {
					cs.forms.set_field('input[name="mod"][form="create_endpoint"]', '');
				});
				
			} else {
				
				// Hide the custom module text input
				$('div[target="popup_new"]').fadeOut('fast');
				
				// Update the hidden input
				cs.forms.set_field('input[type="hidden"][name="mod"]', $(s).val());
			}
		});
	}
	
	/**
	 * Callback: Delete Endpoint
	 */
	cs.register.callback('endpoint.delete', function(c,m,d,a) {
		cs.layout.remove('div[type="row"][endpoint="' + d.uuid + '"]');
	});
	
	/**
	 * Callback: Create Endpoint
	 */
	cs.register.callback('endpoint.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][target="endpoints"]').prepend(cs.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type: 'row',
					target: 'endpoints',
					endpoint: d.uuid,
					children: (function() {
						var cols = [
						    {col: 'select', key: null},
							{col: 'ep_name', key: 'name'},
							{col: 'ep_path', key: 'path'},
							{col: 'ep_action', key: 'action'},
							{col: 'ep_method', key: 'method'},
							{col: 'ep_desc', key: 'desc'},
							{col: 'ep_enabled', key: 'enabled'},
							{col: 'ep_protected', key: 'protected'},
							{col: 'ep_locked', key: 'locked'}
						];
						var c = [];
						$.each(cols, function(i,o) {
							if (o.col == 'ep_name') {
								c.push(cs.layout.create.element('div', {
									css:  'table_col table_link',
									attr: {
										type: 'button',
										action: 'link',
										target: 'admin?panel=endpoints&endpoint=' + d.uuid,
										col: o.col
									},
									text: d.name
								}));
							} else if (o.col == 'ep_locked') {
								c.push(cs.layout.create.element('div', {
									css: 'table_col',
									attr: {
										col: o.col
									},
									text: ''
								}));
							} else if (o.col == 'select') {
								c.push(cs.layout.create.element('div', {
									css: 'table_select_col',
									children: [cs.layout.create.element('input', {
										attr: {
											type: 'radio',
											name: 'endpoint_uuid',
											action: 'update',
											value: d.uuid
										}
									})]
								}));
							} else {
								c.push(cs.layout.create.element('div', {
									css:  'table_col',
									attr: {
										col: o.col
									},
									text: (function() {
										if (o.col == 'ep_enabled') {
											return (d.enabled === true) ? 'Yes': 'No';
										} else {
											return d[o.key]
										}
									})()
								}));
							}
						});
						return c;
					})()
				}
			}));
		}
	});
});