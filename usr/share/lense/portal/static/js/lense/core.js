var lense = (function() {
	var core         = {};
	
	// Modules container
	core.module      = {};
	
	// Constructors / methods / callbacks
	core.constructor = {};
	core.method      = {};
	core.callback    = {};
	
	// Current view
	core.view        = url.param_get('view');
	
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
	 */
	core.import = function(n,m) {
		
		// Module names must be unique
		if (n in core.module) {
			throw new ModuleDefined(n);
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