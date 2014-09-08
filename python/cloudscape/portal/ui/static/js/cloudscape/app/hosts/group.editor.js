cs.import('CSHostGroupEditor', function() { 
	
	// Metadata container / edit window
	this.metadata = null;
	this.window   = null;
	
	/**
	 * Initialize CSHostGroupDetails
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load metadata
		cs.hosts.load();
		
		// Document ready
		$(document).ready(function() {
			cs.hosts.set_layout();
			cs.hosts.bind();
			cs.hosts.set_window();
			
			// Fade in the editor frame and sidebar
			cs.layout.fadein('.editor_frame, .sidebar');
		});
		
		// Window resize
		$(window).resize(function() {
			cs.hosts.set_layout();
		});
	}
	
	/**
	 * Active Host Group
	 */
	this.active = function() {
		return $('input[type="hidden"][name="hgroup_uuid"]').val();
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
	 * Set Host Group Metadata Window
	 */
	this.set_window = function() {
		
		// Set the mode
		mode = 'ace/mode/json';
		
		// Create the editor instance
		cs.hosts.window = ace.edit('hgroup_metadata');
		cs.hosts.window.setTheme('ace/theme/chrome');
		cs.hosts.window.getSession().setMode(mode);
		cs.hosts.window.getSession().setUseWrapMode(true);
		
		// Set the editor contents
		cs.hosts.window.setValue(JSON.stringify(cs.hosts.metadata, null, '\t'), -1);
		
		// Set to read only
		cs.hosts.window.setReadOnly(true);
	}
	
	/**
	 * Load Host Group Metadata
	 */
	this.load = function() {
		
		// Retrieve the host group metadata
		cs.hosts.metadata = (defined(metadata)) ? clone(metadata) : '';
		
		// Delete the containing element
		$('#load_metadata').remove();
	}
	
	/**
	 * Construct Request
	 */
	this.construct_request = function() {
		
		// Data object
		var data = {
			uuid: cs.hosts.active(),
			metadata: cs.hosts.window.getSession().getValue().replace(/(\r\n|\n|\r|\t)/gm,"")
		};
		
		// Construct the member hosts object
		$('div[type="hgroup_members"][managed]').each(function(i,m) {
			if (!defined(data['members'])) {
				data.members = [];
			}
			var a = get_attr(m);
			data.members.push(a.member);
		});
		
		// <input> elements
		$('input[form="edit_hgroup"]').each(function(i,o) {
			var e = $(o);
			data[e.attr('name')] = e.val();
		});
		
		// <select> elements
		$('select[form="edit_hgroup"]').each(function(i,o) {
			var e = $(o);
			data[e.attr('name')] = e.val();
		});
		return data;
	}
	
	/**
	 * Bind Events
	 */
	this.bind = function() {
		
		// Move host group members
		$(document).on('click', '.table_sortable_item', function(e) {
			var a = get_attr(this);
			var i = $(this);
			
			// If editing
			if (cs.hosts.edit()) {
				
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
		edit_height   = $('.content_window').height();
		sidebar_width = $('.sidebar').width();
		edit_width    = $('.content_window').width();
		header_height = $('.page_header_box').actual('outerHeight', {includeMargin:true});
		menu_height   = $('.formula_edit_menu').actual('outerHeight', {includeMargin:true});
		title_height  = $('.table_title').actual('outerHeight', {includeMargin:true})
		editor_height = edit_height - menu_height - header_height;
		
		// Set the editor width and height
		$('.hgroup_edit').height(edit_height);
		$('.table_editor').height(editor_height - 10);
		$('.hgroup_edit').width(edit_width);
		$('.editor_frame').width(edit_width - sidebar_width - 10);
		$('.table_editor').width(edit_width - sidebar_width - 10);
		$('.sidebar').height(editor_height - 20);
		$('.table_sortable_inner').height(editor_height - 10 - $('.table_title').outerHeight(true) - $('.table_panel_title').outerHeight(true) - $('.table_title_inner').outerHeight(true));
		$('.table_window[group="hgroup_details"]').height(editor_height - title_height - 10);
		$('.editor_frame').height(editor_height);
		
		// Set the editor width and height
		$('.editor').height(editor_height - title_height - 10);
		$('.editor').width(edit_width - sidebar_width - 10);
	}
	
	/**
	 * Callback: Save Host Group
	 */
	cs.register.callback('hgroup.save', function(c,m,d,a) {
		if (c == 200) {
			cs.hosts.edit(false);
			
			// Switch the editor to read only
			cs.hosts.window.setReadOnly(true);
			
			// Disable editing elements
			$('div[editing]').each(function(i,o) {
				$(o).attr('editing', 'no');
			});
			
			// <input> elements
			$('input[form="edit_hgroup"]').each(function(i,o) {
				$(o).attr('disabled', '');
			});
			
			// <select> elements
			$('select[form="edit_hgroup"]').each(function(i,o) {
				$(o).attr('disabled', '');
			});
			
			// Switch the buttons
			$('div[type="button"][target="hgroup.edit"]').css('display', 'block').attr('active', 'yes');
			$('div[type="button"][target="hgroup.save"]').css('display', 'none').attr('active', 'no');
		}
	});
	
	/**
	 * Method: Save Host Group
	 */
	cs.register.method('hgroup.save', function() {
		cs.layout.loading(true, 'Updating host group properties...', function() {
			cs.api.request.post({
				path: 'host/group',
				action: 'update',
				_data: cs.hosts.construct_request(),
				callback: {
					id: 'hgroup.save'
				}
			});
		});
	});
	
	/**
	 * Method: Edit Host Group
	 */
	cs.register.method('hgroup.edit', function() {
		cs.hosts.edit(true);
		
		// Switch the editor to write allowed
		cs.hosts.window.setReadOnly(false);
		
		// Enabled editing elements
		$('div[editing]').each(function(i,o) {
			$(o).attr('editing', 'yes');
		});
		
		// <input> elements
		$('input[form="edit_hgroup"]').each(function(i,o) {
			$(o).removeAttr('disabled');
		});
		
		// <select> elements
		$('select[form="edit_hgroup"]').each(function(i,o) {
			$(o).removeAttr('disabled');
		});
		
		// Switch the buttons
		$('div[type="button"][target="hgroup.edit"]').css('display', 'none').attr('active', 'no');
		$('div[type="button"][target="hgroup.save"]').css('display', 'block').attr('active', 'yes');
	});
});