/**
 * CloudScape Base Interface Class
 * 
 * Base JavaScript class for the CloudScape dashbaord. This library is shard between
 * all pages and provides common functionality, such as URL parsing and message rendering.
 */
cs.import('CSBaseInterface', function() {
	
	/**
	 * Initialize CSBaseInterface
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Load modules
		cs.implement('CSBaseURL', 'url');
		cs.implement('CSBaseForms', 'forms');
		cs.implement('CSBaseButton', 'button');
		cs.implement('CSBaseLayout', 'layout');
		cs.implement('CSBaseValidate', 'validate');
		cs.implement('CSBaseRegister', 'register');
		cs.implement('CSBaseD3', 'd3');
		cs.implement('CSBaseIPAddr', 'ipaddr');
		cs.implement('CSBaseFinder', 'finder');
		
		// Centered elements
		centered = ['.popups_container', '.loading_content'];
		
		// Document ready
		$(document).ready(function() {
			
			// Parse the URL and load any rendered forms
			cs.url.parse();
			cs.forms.load();
			
			// Refresh the page layout
			cs.layout.refresh({
				center: centered
			});
			
			// Elements finished loading
			cs.layout.complete();
			
			// Initialize the button handler
			cs.button.handler();
		});
		
		// Window resize
		$(window).resize(function() {
			cs.layout.refresh({
				center: centered
			});
		});
		
		// Bind actions
		cs.base.bind();
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
			if (group != cs.api.client.params.group) {
				cs.layout.loading(true, 'Switching active group...', function() {
					$('#change_group_form').submit();
				});
			}
		});	
	}
});