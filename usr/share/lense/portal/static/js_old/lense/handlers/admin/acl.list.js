lense.import('LenseAdminACLList', function() {
	
	/**
	 * Intialize LenseAdminACLList
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			lense.admin.acl.bind();
			lense.admin.acl.layout();
		});
		
		// Window resize
		$(window).resize(function() {
			lense.admin.acl.layout();
		});
	}
	
	/**
	 * Set Page Layout
	 */
	this.layout = function() {
			
		// Height attributes
		var height = {
			table: 		  $('#acl_list_table').actual('outerHeight', {includeMargin: true}),
			title:		  $('#acl_list_title').actual('outerHeight', {includeMargin: true}),
			header_title: $('div[class="table_headers"][table="acl_list"]').actual('outerHeight', {includeMargin: true})
		}
		
		// Define the height of the rows container
		var rows_height = (height.table - (height.title + height.header_title + 10));
		
		// Set the height of rows container
		$('div[type="rows"][table="acl_list"]').height(rows_height + 'px').css('overflow', 'auto');
	}
	
	/**
	 * Bind Form Events
	 */
	this.bind = function() {
		
		// Changes to the ACL type input
		$('select[name="type"][form="create_acl"]').on('change', function() {
			var u = [];
			$($(this).find('option:selected')).each(function(i,o) {
				if (defined($(o).val())) {
					u.push($(o).val());
				}
			});
			lense.forms.set_field('input[type="hidden"][name="type"]', u.join(','));
		});
		
		// Changes to the endpoints input
		$('select[name="endpoints"][form="create_acl"]').on('change', function() {
			var u = [];
			$($(this).find('option:selected')).each(function(i,o) {
				if (defined($(o).val())) {
					u.push($(o).val());
				}
			});
			lense.forms.set_field('input[type="hidden"][name="endpoints"]', u.join(','));
		});
	}
	
	/**
	 * Callback: Create ACL
	 */
	lense.register.callback('acl.create', function(c,m,d,a) {
		console.log(d);
	});
	
	/**
	 * Callback: Delete ACL
	 */
	lense.register.callback('acl.delete', function(c,m,d,a) {
		lense.layout.remove('div[type="row"][acl="' + d.uuid + '"]');
	});
	
	/**
	 * Method: Delete ACL
	 */
	lense.register.method('acl.delete', function() {
		var s = $('input[type="radio"][name="acl_uuid"]:checked').val();
		if (defined(s)) {
			lense.layout.popup_toggle(false, 'acl.delete', false, function() { 
				lense.layout.loading(true, 'Deleting ACL...', function() {
					lense.api.request.del({
						path: 'gateway/acl',
						_data: {
							uuid: s
						},
						callback: {
							id: 'acl.delete'
						}
					});
				});
			});
		}
	})
});