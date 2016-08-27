lense.import('log.interface', function() {
	var self = this;

	/**
	 * @constructor
	 */
	this.__init__ = function() {
		// lense.implement([]);
	}

  /**
   * Log to console worker
   *
   * @param {String} msg The console message to log
   */
  this._logConsole = function(msg) {
    if (lense.settings.log_enable === true) {
      console.log(msg);
    }
  }

  /**
   * Notify to UI worker
   *
   * @param {String} content A string of content to show
   * @param {Object} content A jQuery HTML object to show
   * @param {Object} options Any UI options
   */
  this._showUI = function(content, options) {

		// Message content
		var message = (function() {
			if (content instanceof jQuery) {
				return content[0].outerHTML;
			} else {
				return content;
			}
		}())

		// Alert type
		var type   = (!$.inArray(getattr(options, 'type', 'default'), [
			'default',
			'info',
			'primary',
			'success',
			'warning',
			'danger'])
		) ? 'default':getattr(options, 'type', 'default');

		// Show in UI if enabled
		if (lense.settings.show_ui_notifications === true) {
			$.notify({
				message: message,
			},{
				type: type,
				placement: {
					from: "bottom",
					align: "right"
				},
				delay: getattr(options, 'delay', 2000)
			});
		}

		// Store in notifications container
		$('#notification-log').append('<div class="alert alert-' + type + '" role="alert">' + message + '</div>');
  }

	/**
	 * Log mapper
	 *
	 * @param {Integer} index The configuration index
	 * @param {Boolean} state The configuration state
	 * @param {String} content A message to log
	 * @param {Object} content A jQuery HTML object to log/display
	 * @param {Object} config The calling methods configuration object
	 * @param {Object} uiOptions Any additional UI notification options
	 */
	this._logMap = function(index, state, content, config, uiOptions) {
		switch(index) {
			case 1:
				if (config[index] === true) {
					self._showUI(content, uiOptions);
				}
				break;
			case 0:
			default:
				if (config[index] === true) {
					self._logConsole(content);
				}
				break;
		}
	}

  /**
   * Debug logger
   *
   * @param {String} content The debug log content as a string
	 * @param {Object} content The debug log content as jQuery HTML
	 * @param {Object} stack The stacktrace of an exception
   */
  this.debug = function(content, stack) {
		$.each(lense.settings.log_debug, function(i,s) {
			self._logMap(i, s, (content + (defined(stack) ? stack:'')), lense.settings.log_debug, {
				type: 'default',
				delay: 2000
			});
		});
  }

	/**
	 * Info logger
	 *
	 * @param {String} content The info log content as a string
	 * @param {Object} content The info log content as jQuery HTML
	 */
	this.info = function(content) {
		$.each(lense.settings.log_info, function(i,s) {
			self._logMap(i, s, content, lense.settings.log_info, {
				type: 'info',
				delay: 2000
			});
		});
	}

	/**
	 * Warning logger
	 *
	 * @param {String} content The warning log content as a string
	 * @param {Object} content The warning log content as jQuery HTML
	 */
	this.warn = function(content) {
		$.each(lense.settings.log_warn, function(i,s) {
			self._logMap(i, s, content, lense.settings.log_warn, {
				type: 'warning',
				delay: 2000
			});
		});
	}

	/**
	 * Danger logger
	 *
	 * @param {String} content The danger log content as a string
	 * @param {Object} content The danger log content as jQuery HTML
	 */
	this.danger = function(content) {
		$.each(lense.settings.log_danger, function(i,s) {
			self._logMap(i, s, content, lense.settings.log_danger, {
				type: 'danger',
				delay: 2000
			});
		});
	}
	/**
	 * UI notifier
	 *
	 * @param {String} content The UI content as a string
	 * @param {Object} content The UI content as jQuery HTML
	 * @param {Object} options Any additional notification options
	 */
	this.ui = function(content, options) {
		self._showUI(content, options);
	}

	/**
	 * API notifier
	 *
	 * @param {Object} response The API ResponseObject instance
	 */
	this.api = function(response) {
		if (lense.settings.log_api === true) {
			self._showUI($('<div><strong>HTTP ' + response.code + '</strong>: ' + response.message + '</div>')[0].outerHTML, {
				type: (response.code === 500) ? 'danger':response.type,
				delay: 2000
			});
		}
	}
});
