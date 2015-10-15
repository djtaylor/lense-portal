/**
 * Lense Base Interface Class
 * 
 * Base JavaScript class for the Lense dashbaord. This library is shard between
 * all pages and provides common functionality, such as URL parsing and message rendering.
 */
lense.import('LenseBaseInterface', function() {
	
	/**
	 * Initialize LenseBaseInterface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load modules
		lense.implement('LenseBaseURL', 'url');
		lense.implement('LenseBaseForms', 'forms');
		lense.implement('LenseBaseButton', 'button');
		lense.implement('LenseBaseLayout', 'layout');
		lense.implement('LenseBaseValidate', 'validate');
		lense.implement('LenseBaseRegister', 'register');
		lense.implement('LenseBaseIPAddr', 'ipaddr');
		lense.implement('LenseBaseFinder', 'finder');
		
		// Centered elements
		centered = ['.popups_container', '.loading_content'];
		
		// Document ready
		$(document).ready(function() {
			
			// Parse the URL and load any rendered forms
			lense.url.parse();
			lense.forms.load();
			
			// Refresh the page layout
			lense.layout.refresh({
				center: centered
			});
			
			// Elements finished loading
			lense.layout.complete();
			
			// Initialize the button handler
			lense.button.handler();
		});
		
		// Window resize
		$(window).resize(function() {
			lense.layout.refresh({
				center: centered
			});
		});
		
		// Bind actions
		lense.base.bind();
	}
	
	/**
	 * Bind Global Actions
	 */
	this.bind = function() {
		
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
		
		// Change active group
		$('select[id="active_group"][name="group"]').change(function() {
			var group = $(this).val();
			
			// If actually changing groups
			if (group != lense.api.client.params.group) {
				lense.layout.loading(true, 'Switching active group...', function() {
					$('#change_group_form').submit();
				});
			}
		});	
	}
});