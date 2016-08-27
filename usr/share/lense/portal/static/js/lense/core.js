// Core constructor
var lense = (function() {
	var core         = {};

	// Modules container
	core.module      = {};

	// Constructors / methods / callbacks
	core.constructor = {};
	core.method      = {};
	core.callback    = {};

	/**
	 * Raise and show critical error and abort
	 *
	 * @param {String} e The error to raise
	 * @param {Object} Error An alternate exception object (optional)
	 */
	core.raise = function(e, exc) {

		// Show the error to the user
		lense.log.error(e);

		// Raise the exception
		var exc = (!defined(exc) ? Error:exc);
		throw new exc(e);
	}

	/**
	 * Settings object
	 *
	 * @param {Bool} log_enable Log to the console
	 * @param {Bool} log_debug.0 Log debug messages to the console
	 * @param {Bool} log_debug.1 Show debug messages in the UI
	 * @param {Bool} log_info.0 Log info messages to the console
	 * @param {Bool} log_info.1 Show info messages in the UI
	 * @param {Bool} show_ui_notifications Global toggle for UI messages
	 */
	core.settings    = {
		log_enable: true,
		log_debug: [true, false],
		log_info: [true, true],
		log_warn: [true, true],
		log_danger: [true, true],
		log_api: true,
		show_ui_notifications: true
	},

	// Current view
	core.view        = url.param_get('view');

	// URL management
	core.url         = new function() {
		var inner = this;

		/**
		 * Check if URL contains parameter
		 *
		 * @param {String} key The URL key to check
		 */
		this.hasParam = function(key) {
			var re = new RegExp('[&\?]{1}' + key, 'g');
			return (window.location.search.match(re)) ? true : false;
		}

		/**
		 * Get URL parameter
		 *
		 * @param {String} key The query key to look for
		 * @param {*} def A default value to use if no key found
		 */
		this.getParam = function(key, def) {
			return decodeURIComponent((new RegExp('[?|&]' + key + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||def;
		}

		/**
		 * Delete URL parameter
		 *
		 * @param {String} key The query key to delete
		 */
		this.delParam = function(key) {
			var sourceURL = window.location.href;
			var new_url   = sourceURL.split("?")[0],
	        	param,
	        	params_arr = [],
	        	queryString = (sourceURL.indexOf("?") !== -1) ? sourceURL.split("?")[1] : "";
		    if (queryString !== "") {
		        params_arr = queryString.split("&");
		        for (var i = params_arr.length - 1; i >= 0; i -= 1) {
		            param = params_arr[i].split("=")[0];
		            if (param === key) {
		                params_arr.splice(i, 1);
		            }
		        }
		        new_url = new_url + "?" + params_arr.join("&");
		    }
		    history.pushState(null, null, new_url);
		}

		/**
		 * Set URL parameter
		 *
		 * @param {String} key The query key to set
		 * @param {String|Boolean} value The parameter value
		 */
		this.setParam = function(key, value) {
			key = encodeURI(key); value = encodeURI(value);
			var kvp = document.location.search.substr(1).split('&');
			var i=kvp.length; var x; while(i--) {
		        x = kvp[i].split('=');
		        if (x[0]==key) {
		            x[1] = value;
		            kvp[i] = x.join('=');
		            break;
		        }
		    }
			if(i<0) {kvp[kvp.length] = [key,value].join('=');}
			var base_url   = window.location.href.match(/^[^\#\?]+/)[0];
			var new_params = '?' + kvp.join('&');
			var new_url    = base_url + new_params
			history.pushState(null, null, new_url);
		}

		/**
		 * Parse the URL looking for events
		 */
		this.parseEvents = function() {

			// Define persistent and notification URL parameters
			var url_objects = {
				"persistent": [ 'view', 'edit', 'create', 'uuid'],
				"notify":     [ 'status', 'body' ]
			};

			// Object notification parameters
			url_objects.notify.forEach(function(notify) {
				var notify_param = inner.getParam(notify);
				if (notify_param !== null) {
					var current_url = window.location.pathname;
					var base_url    = window.location.href.match(/^[^\#\?]+/)[0];
					var base_sep	= '?'
					var new_url     = base_url;
					url_objects.persistent.forEach(function(param_type) {
						var param_val = inner.getParam(param_type);
						if (param_val !== null) {
							new_url = new_url + base_sep + param_type + '=' + param_val;
						}
						base_sep = '&';
					});
					history.pushState(null, null, new_url);
				}
			});
		}
	};

	// Generate UUID4
	core.uuid4 = function() {
		function s4() {
			return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
		}
		return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
	},

	/**
	 * Show Growl style notification
	 *
	 * @param {String} type The notification type
	 * @param {String} msg The notification message
	 */
	 core.notify = function(type, message) {
		 $.notify({
			 message: message,
		 },{
			 type: type,
			 placement: {
				 from: "bottom",
				 align: "right"
			 },
			 delay: 1000
		 });

		 // Notification log
		 $('#notification-log').append('<div class="alert alert-' + type + '" role="alert">' + message + '</div>');
	 }

	/**
	 * Local Preferences
	 */
	core.preferences = {

		/**
		 * Get Preference
		 *
		 * Retrieve a local preference.
		 *
		 * @param {k} The preference key
		 * @param {d} A default value
		 */
		get: function(k,d) {
			return getattr(Cookies.get(), 'pref_' + k, d);
		},

		/**
		 * Set Preference
		 *
		 * Set a local preference.
		 *
		 * @param {k} The preference key
		 * @param {v} The preference value
		 */
		set: function(k,v) {
			Cookies.set('pref_' + k, v);
		},

		/**
		 * Initialize Preference
		 *
		 * Initialize a preference key with a default if not already set
		 *
		 * @param {k} The preference key
		 * @param {v} The preference initial value
		 */
		init: function(k,v) {
			function inner(_k,_v) {
				if (!hasattr(Cookies.get(), 'pref_'+ _k)) {
					Cookies.set('pref_' + _k, _v)
				}
			}
			if ($.type(k) === "object") {
				$.each(k, function(ek,ev) {
					inner(ek,ev);
				})
			} else {
				inner(k,v);
			}
		}
	},

	/**
	 * Object Registration
	 */
	core.register = {

		/**
		 * Register Callback
		 *
		 * Register a method used to handle a SocketIO response.
		 *
		 * @param {n} The name of the callback
		 * @param {m} The callback method
		 */
		callback: function(n,m) {
			core.callback[n] = m;
		},

		/**
		 * Register Method
		 *
		 * Register a generic method.
		 *
		 * @param {n} The name of the method reference
		 * @param {m} The method object
		 */
		method: function(n,m) {
			core.method[n] = m;
		},

		/**
		 * Register Constructor
		 *
		 * Register a constructor method to be called after bootstrapping.
		 *
		 * @param {n} The name of the constructor
		 * @param {m} The constructor method
		 */
		constructor: function(n,m) {
			core.constructor[n] = m;
		},
	};

	/**
	 * Import Module
	 *
	 * Import an included module into the Lense namespace. This assumes that the parent
	 * namespace has already been initialized.
	 *
	 * @param {n} The name of the module
	 * @param {m} The module contents
	 * @param {c} The module constructor method
	 */
	core.import = function(n,m,c) {

		// Module names must be unique
		if (n in core.module) {
			throw new ModuleDefined(n);
		}

		// Load the constructor
		if (defined(c)) {
			core.register.constructor(n,c);
		}

		// Import the module object / store includes
		core.module[n] = m;
	};

	/**
	 * Bootstrap Interfaces
	 *
	 * Bootstrap JavaScript module interfaces.
	 *
	 * @param {c} Interface modules
	 */
	core.bootstrap = function(c) {

		// Extended data elements
		$.each(['x-var'], function(i,e) {
			document.registerElement(e);
		});

		// Process interfaces
		$.each(c, function(k,v) {
			lib  = v.split('.');
			path = lib[0];
			name = lib[1];

			// Create a new class instance
			core.implement(v, true);
		});

		// Run constructors
		core._construct();
	};

	/**
	 * Implement Module (Private)
	 */
	core._implement = function(n,i) {
		var mod = (($.isArray(n)) ? n[0]: n);

		// Parameterized implementation
		if ($.isArray(n)) {

			// Filter by view
			if (('view' in n[1]) && (n[1].view != lense.view)) {
				return;
			}
		}

		// Could not locate the module
		if (!core.module.hasOwnProperty(mod)) {
			throw new ModuleNotFound(mod);
		}

		// Module object / namespace
		module = new core.module[mod]();
		nspace = mod.split('.');

		// Initialize the root namespace
		if (!core.hasOwnProperty(nspace[0])) {
			core[nspace[0]] = {}
		}

		// Loading a module interface
		if (i === true) {
			core[nspace[0]] = module;

		// Loading a child module
		} else {
			core[nspace[0]][nspace[1]] = module;
		}

		// Construct the module
		(function() {

			// Call initialization method if it exists
			if (module.hasOwnProperty('__init__')) {
				module.__init__();
			} else {
				module.__init__ = undefined;
			}
		}());
	}

	/**
	 * Implement Module (Public)
	 *
	 * Extend the current namespace with a new module object.
	 *
	 * @param {n}    The module name or an array of modules
	 * @param {i}    Is this a module interface
	 */
	core.implement = function(n,i) {

		// Array of module
		if ($.isArray(n)) {
			$.each(n, function(i,k) {
				core._implement(k);
			})

		// Single module
		} else {
			core._implement(n,i);
		}
	};

	/**
	 * Run Constructors
	 */
	core._construct = function() {

		// Wait for SocketIO connection
		if ((defined(lense.api)) && (lense.api.status === 'connected')) {
			$.each(core.constructor, function(n,m) {
				new m();
			});

	    // Socket still connecting, wait
	    } else {
	    	window.setTimeout(core._construct, 20);
	    }
	};

	// Return the global namespace
	return core;
})();
