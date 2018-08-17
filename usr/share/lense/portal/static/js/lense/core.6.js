class LensePreferences {

	/**
	 * Get Preference
	 *
	 * Retrieve a local preference.
	 *
	 * @param {k} The preference key
	 * @param {d} A default value
	 */
	get(k,d) {
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
	set(k,v) {
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
	init(k,v) {
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
}

class Lense {
	constructor() {

		// The current view URL parameter
		this.view 			 = url.param_get('view');

		// Modules container
		this.module      = {};

		// Pre-bootstrap modules
		this.modulePre   = {};

		// Constructors / methods / callbacks
		this.constructor = {};
		this.method      = {};
		this.callback    = {};

		/**
		 * Cookie Preferences
		 */
		this.preferences = new LensePreferences();

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
		this.settings    = {
			log_enable: true,
			log_debug: [true, false],
			log_info: [true, true],
			log_warn: [true, true],
			log_danger: [true, true],
			log_api: true,
			show_ui_notifications: true
		}
	}

	/**
	 * Raise and show critical error and abort
	 *
	 * @param {String} e The error to raise
	 * @param {Object} Error An alternate exception object (optional)
	 */
	raise(e, exc = Error) {

		// Show the error to the user
		this.notify('danger', e);

		// Raise the exception
		throw new exc(e);
	}

	/**
	 * Generate UUID4 String
	 */
	uuid4() {
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
	notify(type, message) {
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

}

var lense = new Lense();

// Core constructor
var lense = (function() {

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
	 * @param {String} n The name of the module
	 * @param {Object} m The module contents
	 * @param {Bool} p Run in the pre-bootstrap phase
	 */
	core.import = function(n,m,p) {

		// Module names must be unique
		if (n in core.module) {
			throw new ModuleDefined(n);
		}

		// Import the module object / store includes
		if (p === true) {
			core.modulePre[n] = m;
		} else {
			core.module[n] = m;
		}
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
