lense.import('api.response', function() {
	var self = this;

	/**
	 * Response Object
	 *
	 @ @param {Object} response The response object
	 */
	this.Object = function(response) {
		var inner    = this;
		var content  = JSON.parse(response.content);

		// Public attributes
		this.type     = ($.inArray(getattr(response, 'type'), ['success', 'error'])) ? 'default': getattr(response, 'type');
		this.message  = getattr(content, 'message');
		this.code     = getattr(response, 'code');
		this.data     = getattr(content, 'data', null);
		this.callback = getattr(content, 'callback', null);

		/**
		 * @constructor
		 */
		(function() {

			// Run the callback
			if (defined(inner.callback)) {

				// Request failed
				if (inner.code !== 200) {
					lense.log.api(inner);

				// Request OK
				} else {

					// Callback uses a key argument
					if (inner.callback.contains('+')) {
						var attrs = inner.callback.split('+');
						lense.callback[attrs[0]](attrs[1], inner.data);
					} else {
						lense.callback[inner.callback](inner.data);
					}
				}

			// No callback, notify
			} else {
				lense.log.api(inner);
			}
		}());
	}

	/**
	 * API Update Callback
	 */
	lense.register.callback('update', function(d) {
		console.log('update');
	});

	/**
	 * API Support Callback
	 */
	lense.register.callback('getAPISupport', function(d) {
		lense.api.support = d.contents;
	});

	/**
	 * Server Version Callback
	 */
	lense.register.callback('getServerVersion', function(d) {
		lense.api.server = d.contents;
		$('input.socketio-server').val(lense.api.server);
	});
});
