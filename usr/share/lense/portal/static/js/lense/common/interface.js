lense.import('common.interface', function() {
	
	/**
	 * Initialize Interface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load modules
		$.each([
		    'common.url',
		    'common.forms',
		    'common.button',
		    'common.layout',
		    'common.validate',
		    'common.register',
		    'common.ipaddr',
		    'common.finder'
		], function(i,k) {
			lense.implement(k);
		});
		
		// Centered elements
		centered = ['.popups_container', '.loading_content'];
		
		// Document ready
		$(document).ready(function() {
			
			// Parse the URL and load any rendered forms
			lense.common.url.parse();
			lense.common.forms.load();
			
			// Refresh the page layout
			lense.common.layout.refresh({
				center: centered
			});
			
			// Elements finished loading
			lense.common.layout.complete();
			
			// Initialize the button handler
			lense.common.button.handler();
		});
		
		// Window resize
		$(window).resize(function() {
			lense.common.layout.refresh({
				center: centered
			});
		});
		
		// Bind actions
		lense.common._bind();
	}
	
	/**
	 * Bind Global Actions
	 */
	this._bind = function() {
		
		// Show/hide API key
		$(document).on('click', '.nav_profile_api_key_toggle', function() {
			var a = get_attr(this);
			
			// Show API key
			if (a.state == 'show') {
				$('input[name="api_key"]').attr('type', 'text');
				$(this).attr('state', 'hide');
			}
			
			// Hide API key
			if (a.state == 'hide') {
				$('input[name="api_key"]').attr('type', 'password');
				$(this).attr('state', 'show');
			}
		});
		
		// Click logout button
		$(document).on('click', '.nav_profile_logout', function() {
			$.each(lense.api.client.keys, function(i,k) {
				Cookies.remove(k);
			});
			
			// Submit the logout form
			$('#logout_form').submit();
		});
		
		// Change active group
		$('select[id="active_group"][name="group"]').change(function() {
			var group = $(this).val();
			
			// If actually changing groups
			if (group != lense.api.client.params.group) {
				lense.common.layout.loading(true, 'Switching active group...', function() {
					$('#change_group_form').submit();
				});
			}
		});	
	}
});