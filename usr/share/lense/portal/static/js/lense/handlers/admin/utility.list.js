lense.import('LenseAdminUtilitiesList', function() {
	
	/**
	 * Initialize LenseAdminUtilityList
	 * @constructor
	 */
	this.__init__ = function() {

		// Document ready
		$(document).ready(function() {
			lense.admin.utility.bind();
			lense.admin.utility.layout();
		});
		
		// Window resize
		$(window).resize(function() {
			lense.admin.utility.layout();
		});
	}
	
	/**
	 * Set Page Layout
	 */
	this.layout = function() {
		
		// Height attributes
		var height = {
			table: 		  $('#utility_list_table').actual('outerHeight', {includeMargin: true}),
			title:		  $('#utility_list_title').actual('outerHeight', {includeMargin: true}),
			header_title: $('div[class="table_headers"][table="utility_list"]').actual('outerHeight', {includeMargin: true})
		}
		
		// Define the height of the rows container
		var rows_height = (height.table - (height.title + height.header_title + 10));
		
		// Set the height of rows container
		$('div[type="rows"][table="utility_list"]').height(rows_height + 'px').css('overflow', 'auto');
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
		$('select[name="util_method"][form="create_utility"]').on('change', function() {
			var s = $(this).find('option:selected');
			lense.forms.set_field('input[type="hidden"][name="util_method"]', $(s).val());
		});
		
		// Changes to the enabled input
		$('select[name="enabled"][form="create_utility"]').on('change', function() {
			var s = $(this).find('option:selected');
			lense.forms.set_field('input[type="hidden"][name="enabled"]', $(s).val());
		});
		
		// Changes to the protected input
		$('select[name="protected"][form="create_utility"]').on('change', function() {
			var s = $(this).find('option:selected');
			lense.forms.set_field('input[type="hidden"][name="protected"]', $(s).val());
		});
		
		// Changes to the external utilities input
		$('select[name="utils"][form="create_utility"]').on('change', function() {
			var u = [];
			$($(this).find('option:selected')).each(function(i,o) {
				if (defined($(o).val())) {
					u.push($(o).val());
				}
			});
			lense.forms.set_field('input[type="hidden"][name="utils"]', u.join(','));
		});
		
		// Select a module
		$('select[name="mod"][form="create_utility"]').on('change', function() {
			var s = $(this).find('option:selected');
			
			// Custom module
			if ($(s).val() == 'new') {
				
				// Show the custom module text input
				$('div[target="popup_new"]').fadeIn('fast', function() {
					lense.forms.set_field('input[name="mod"][form="create_utility"]', '');
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
	 * Callback: Delete Utility
	 */
	lense.register.callback('utility.delete', function(c,m,d,a) {
		lense.layout.remove('div[type="row"][utility="' + d.uuid + '"]');
	});
	
	/**
	 * Callback: Create Utility
	 */
	lense.register.callback('utility.create', function(c,m,d,a) {
		if (c == 200) {
			$('div[type="rows"][target="utilities"]').prepend(lense.layout.create.element('div', {
				css:  'table_row',
				attr: {
					type: 'row',
					target: 'utilities',
					utility: d.uuid,
					children: (function() {
						var cols = [
						    {col: 'select', key: null},
							{col: 'util_path', key: 'path'},
							{col: 'util_action', key: 'action'},
							{col: 'util_method', key: 'method'},
							{col: 'util_desc', key: 'desc'},
							{col: 'util_enabled', key: 'enabled'},
							{col: 'util_protected', key: 'protected'},
							{col: 'util_locked', key: 'locked'}
						];
						var c = [];
						$.each(cols, function(i,o) {
							if (o.col == 'util_name') {
								c.push(lense.layout.create.element('div', {
									css:  'table_col table_link',
									attr: {
										type: 'button',
										action: 'link',
										target: 'admin?panel=utilities&utility=' + d.uuid,
										col: o.col
									},
									text: d.name
								}));
							} else if (o.col == 'util_locked') {
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
											name: 'utility_uuid',
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
										if (o.col == 'util_enabled') {
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