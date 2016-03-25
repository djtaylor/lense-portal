lense.import('Admin_HandlerList', function() {
	
	/**
	 * Initialize LenseAdminUtilityList
	 * @constructor
	 */
	this.__init__ = function() {

		// Document ready
		$(document).ready(function() {
			lense.admin.handler.bind();
			lense.admin.handler.layout();
		});
		
		// Window resize
		$(window).resize(function() {
			lense.admin.handler.layout();
		});
	}
	
	/**
	 * Set Page Layout
	 */
	this.layout = function() {
		
		// Height attributes
		var height = {
			table: 		  $('#handler_list_table').actual('outerHeight', {includeMargin: true}),
			title:		  $('#handler_list_title').actual('outerHeight', {includeMargin: true}),
			header_title: $('div[class="table_headers"][table="handler_list"]').actual('outerHeight', {includeMargin: true})
		}
		
		// Define the height of the rows container
		var rows_height = (height.table - (height.title + height.header_title + 10));
		
		// Set the height of rows container
		$('div[type="rows"][table="handler_list"]').height(rows_height + 'px').css('overflow', 'auto');
	}
	
	/**
	 * Bind Form Events
	 */
	this.bind = function() {
			
		// Changes to new module input
		$('input[type="text"][name="mod_new"]').on('input', function() {
			
			// Update the hidden input
			lense.forms.set_field('input[type="hidden"][name="mod"]', $(this).val());
		});
		
		// Changes to the method input
		$('select[name="handler_method"][form="create_handler"]').on('change', function() {
			var s = $(this).find('option:selected');
			lense.forms.set_field('input[type="hidden"][name="handler_method"]', $(s).val());
		});
		
		// Changes to the enabled input
		$('select[name="enabled"][form="create_handler"]').on('change', function() {
			var s = $(this).find('option:selected');
			lense.forms.set_field('input[type="hidden"][name="enabled"]', $(s).val());
		});
		
		// Changes to the protected input
		$('select[name="protected"][form="create_handler"]').on('change', function() {
			var s = $(this).find('option:selected');
			lense.forms.set_field('input[type="hidden"][name="protected"]', $(s).val());
		});
		
		// Changes to the external handlers input
		$('select[name="utils"][form="create_handler"]').on('change', function() {
			var u = [];
			$($(this).find('option:selected')).each(function(i,o) {
				if (defined($(o).val())) {
					u.push($(o).val());
				}
			});
			lense.forms.set_field('input[type="hidden"][name="utils"]', u.join(','));
		});
		
		// Select a module
		$('select[name="mod"][form="create_handler"]').on('change', function() {
			var s = $(this).find('option:selected');
			
			// Custom module
			if ($(s).val() == 'new') {
				
				// Show the custom module text input
				$('div[target="popup_new"]').fadeIn('fast', function() {
					lense.forms.set_field('input[name="mod"][form="create_handler"]', '');
				});
				
			} else {
				
				// Hide the custom module text input
				$('div[target="popup_new"]').fadeOut('fast');
				
				// Update the hidden input
				lense.forms.set_field('input[type="hidden"][name="mod"]', $(s).val());
			}
		});
	}
	
	/**
	 * Callback: Delete Handler
	 */
	lense.register.callback('handler.delete', function(c,m,d,a) {
		lense.layout.remove('div[type="row"][handler="' + d.uuid + '"]');
	});
	
	/**
	 * Callback: Create Handler
	 */
	lense.register.callback('handler.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][target="handlers"]').prepend(lense.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type: 'row',
					target: 'handlers',
					handler: d.uuid,
					children: (function() {
						var cols = [
						    {col: 'select', key: null},
							{col: 'handler_path', key: 'path'},
							{col: 'handler_action', key: 'action'},
							{col: 'handler_method', key: 'method'},
							{col: 'handler_desc', key: 'desc'},
							{col: 'handler_enabled', key: 'enabled'},
							{col: 'handler_protected', key: 'protected'},
							{col: 'handler_locked', key: 'locked'}
						];
						var c = [];
						$.each(cols, function(i,o) {
							if (o.col == 'handler_name') {
								c.push(lense.layout.create.element('div', {
									css:  'table_col table_link',
									attr: {
										type: 'button',
										action: 'link',
										target: 'admin?panel=handlers&handler=' + d.uuid,
										col: o.col
									},
									text: d.name
								}));
							} else if (o.col == 'handler_locked') {
								c.push(lense.layout.create.element('div', {
									css: 'table_col',
									attr: {
										col: o.col
									},
									text: ''
								}));
							} else if (o.col == 'select') {
								c.push(lense.layout.create.element('div', {
									css: 'table_select_col',
									children: [lense.layout.create.element('input', {
										attr: {
											type: 'radio',
											name: 'handler_uuid',
											action: 'update',
											value: d.uuid
										}
									})]
								}));
							} else {
								c.push(lense.layout.create.element('div', {
									css:  'table_col',
									attr: {
										col: o.col
									},
									text: (function() {
										if (o.col == 'handler_enabled') {
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