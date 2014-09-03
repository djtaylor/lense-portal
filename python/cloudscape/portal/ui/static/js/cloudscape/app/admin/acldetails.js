cs.import('CSAdminACLDetails', function() {
	
	/**
	 * Intialize CSAdminACLDetails
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			cs.admin.acl.set_layout();
			cs.admin.acl.bind();
		});
		
		// Window Resize
		$(window).resize(function() {
			cs.admin.acl.set_layout();
		});
	}
	
	/**
	 * Active ACL
	 */
	this.active = function() {
		return $('input[type="hidden"][name="acl_uuid"]').val();
	}
	
	/**
	 * Edit State
	 */
	this.edit = function(s) {
		if (s === true || s === false) {
			$('input[type="hidden"][name="edit"]').val((s === true) ? 'yes': 'no');
		} else {
			return ($('input[type="hidden"][name="edit"]').val() === 'yes') ? true : false;
		}
	}
	
	/**
	 * Construct Request
	 */
	this.construct_request = function() {
		
		// Data object
		var data = {
			uuid: cs.admin.acl.active(),
			endpoints: {
				global: [],
				object: [],
				host:   []
			}
		};
		
		// Construct the managed endpoints object
		$('div[group="acl_endpoints"][acl_type]').each(function(i,g) {
			var ga = get_attr(g);
			$($('#acl_' + ga.acl_type + '_managed').find('.table_sortable_item')).each(function(i,e) {
				data.endpoints[ga.acl_type].push($(e).attr('endpoint'));
			});
		});
		
		// <input> elements
		$('input[form="edit_acl"]').each(function(i,o) {
			var e = $(o);
			data[e.attr('name')] = e.val();
		});
		
		// <select> elements
		$('select[form="edit_acl"]').each(function(i,o) {
			var e = $(o);
			data[e.attr('name')] = (function() {
				b = e.val().split(':');
				return (b[1] === 'true') ? true : false;
			})();
		});
		return data;
	}
	
	/**
	 * Bind Events
	 */
	this.bind = function() {
		
		// Jump to another ACL
		$('select[name="acl_jump"]').on('change', function() {
			if (cs.admin.acl.active() != this.value) {
				window.location = '/portal/admin?panel=acls&acl=' + this.value;
			}
		});
		
		// Move endpoints
		$(document).on('click', '.table_sortable_item', function(e) {
			var a = get_attr(this);
			var i = $(this);
			
			// If editing
			if (cs.admin.acl.edit()) {
				
				// Available
				if (a.hasOwnProperty('available')) {
					$(this).detach().appendTo('#' + a.type + '_managed').removeAttr('available').attr('managed', '');
					$(this).find('.table_sortable_icon').attr('icon', 'remove');
				}
				
				// Managed
				if (a.hasOwnProperty('managed')) {
					$(this).detach().appendTo('#' + a.type + '_available').removeAttr('managed').attr('available', '');
					$(this).find('.table_sortable_icon').attr('icon', 'add');
				}
			}
		});
	}
	
	/**
	 * Set Details Layout
	 */
	this.set_layout = function() {
		edit_height   = ($(window).height() - $('.base_nav').height()) - 20;
		sidebar_width = $('.sidebar').width();
		edit_width    = ($(window).width() - 20);
		header_height = $('.page_header_box').height();
		menu_height   = $('.formula_edit_menu').height();
		editor_height = edit_height - menu_height - header_height - 20;
		
		
		// Set the editor width and height
		$('.acl_edit').height(edit_height);
		$('.editor_frame').height(editor_height);
		$('.table_editor').height(editor_height - 10);
		$('.acl_edit').width(edit_width);
		$('.editor_frame').width(edit_width - sidebar_width - 10);
		$('.table_editor').width(edit_width - sidebar_width - 10);
		$('.sidebar').height(editor_height - 20);
		$('.table_sortable_inner').height(editor_height - 10 - $('.table_title').outerHeight(true) - $('.table_panel_title').outerHeight(true) - $('.table_title_inner').outerHeight(true));
	
		// Fade in the editor frame
		cs.layout.fadein('.editor_frame');
	}
	
	/**
	 * Callback: Save ACL
	 */
	cs.register.callback('acl.save', function(c,m,d,a) {
		if (c == 200) {
			cs.admin.acl.edit(false);
			
			// Disable editing elements
			$('div[editing]').each(function(i,o) {
				$(o).attr('editing', 'no');
			});
			
			// <input> elements
			$('input[form="edit_acl"]').each(function(i,o) {
				$(o).attr('disabled', '');
			});
			
			// <select> elements
			$('select[form="edit_acl"]').each(function(i,o) {
				$(o).attr('disabled', '');
			});
			
			// Switch the buttons
			$('div[type="button"][target="acl.edit"]').css('display', 'block').attr('active', 'yes');
			$('div[type="button"][target="acl.save"]').css('display', 'none').attr('active', 'no');
		}
	});
	
	/**
	 * Method: Save ACL
	 */
	cs.register.method('acl.save', function() {
		cs.layout.loading(true, 'Updating ACL properties...', function() {
			cs.api.request.post({
				path: 'auth/acl',
				action: 'update',
				_data: cs.admin.acl.construct_request(),
				callback: {
					id: 'acl.save'
				}
			});
		});
	});
	
	/**
	 * Method: Edit ACL
	 */
	cs.register.method('acl.edit', function() {
		cs.admin.acl.edit(true);
		
		// Enabled editing elements
		$('div[editing]').each(function(i,o) {
			$(o).attr('editing', 'yes');
		});
		
		// <input> elements
		$('input[form="edit_acl"]').each(function(i,o) {
			$(o).removeAttr('disabled');
		});
		
		// <select> elements
		$('select[form="edit_acl"]').each(function(i,o) {
			$(o).removeAttr('disabled');
		});
		
		// Switch the buttons
		$('div[type="button"][target="acl.edit"]').css('display', 'none').attr('active', 'no');
		$('div[type="button"][target="acl.save"]').css('display', 'block').attr('active', 'yes');
	});
});