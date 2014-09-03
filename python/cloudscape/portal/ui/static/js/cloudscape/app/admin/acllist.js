cs.import('CSAdminACLList', function() {
	
	/**
	 * Intialize CSAdminACLList
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			cs.admin.acl.bind();
			cs.admin.acl.layout();
		});
		
		// Window resize
		$(window).resize(function() {
			cs.admin.acl.layout();
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
			cs.forms.set_field('input[type="hidden"][name="type"]', u.join(','));
		});
		
		// Changes to the endpoints input
		$('select[name="endpoints"][form="create_acl"]').on('change', function() {
			var u = [];
			$($(this).find('option:selected')).each(function(i,o) {
				if (defined($(o).val())) {
					u.push($(o).val());
				}
			});
			cs.forms.set_field('input[type="hidden"][name="endpoints"]', u.join(','));
		});
	}
	
	/**
	 * Callback: Create ACL
	 */
	cs.register.callback('acl.create', function(c,m,d,a) {
		console.log(d);
	});
	
	/**
	 * Callback: Delete ACL
	 */
	cs.register.callback('acl.delete', function(c,m,d,a) {
		cs.layout.remove('div[type="row"][acl="' + d.uuid + '"]');
	});
	
	/**
	 * Method: Delete ACL
	 */
	cs.register.method('acl.delete', function() {
		var s = $('input[type="radio"][name="acl_uuid"]:checked').val();
		if (defined(s)) {
			cs.layout.popup_toggle(false, 'acl.delete', false, function() { 
				cs.layout.loading(true, 'Deleting ACL...', function() {
					cs.api.request.post({
						path: 'auth/acl',
						action: 'delete',
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