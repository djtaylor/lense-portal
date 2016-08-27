lense.import('common.interface', function() {
	var self = this;

	/**
	 * Inspect Object Callback
	 */
	lense.register.callback('inspectObject', function(data) {
		lense.common.template.render('#object-inspection-permissions', 'object_permissions', data);
	});

	/**
	 * Initialize Interface
	 * @constructor
	 */
	this.__init__ = function() {

		// Initialize preferences
		lense.preferences.init({
			layout: 'list'
		});

		// Load modules
		lense.implement([
		    'common.url',
		    'common.forms',
		    'common.layout',
		    'common.template',
		    'common.ace',
		    'common.object'
		]);

		// Document ready
		$(document).ready(function() {

			// Parse the URL and load any rendered forms
			lense.common.url.parse();
		});

		// Bind actions
		self._bind();
	}

	/**
	 * Bind Global Actions
	 */
	this._bind = function() {

		// Inspect object
		$(document).on('click', 'button[inspect]', function() {
			var uuid = get_attr(this).inspect;
			$('#object-inspection-uuid').text(uuid);
			lense.api.request.submit('permissions_get', { 'object_uuid': uuid }, 'inspectObject');
		});

		// Change layout
		$(document).on('click', '.toggle-layout', function() {
			var layout = get_attr(this).layout;
			$('.layout-container').css('display', 'none');
			$('.layout-' + layout).css('display', 'block');
			lense.preferences.set('layout', layout);
		});

		// Click logout button
		$(document).on('click', '#form-logout-button', function() {
			$.each(lense.api.client.cookies, function(i,k) {
				Cookies.remove(k);
			});

			// Submit the logout form
			$('#form-logout').submit();
		});
	}
});
