var lense = (function() {
	var core      = {};
	
	// Modules container
	core.module   = {};
	
	// Includes container
	core.includes = {};
	
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
		core.includes[n] = m;
	};
	
	/**
	 * Bootstrap Interfaces
	 * 
	 * Bootstrap JavaScript module interfaces.
	 * 
	 * @param {c} Interface modules
	 */
	core.bootstrap = function(c) {
		
		// Wait for all includes to complete
		(function() {
			$.each(core.includes, function(n,i) {
				(function wait_inner(n) {
					setTimeout(function() {
						if (!core.module.hasOwnProperty(n)) {
							wait_inner(n);
						} else {
							core.includes[n] = true;
						}
					}, 10);
				})(n);
			});
			
			// All included
			return true;
		})();
		
		// Bootstrap after includes completed
		(function() {
			(function wait_inner() {
				setTimeout(function() {
					var a = true;
					$.each(core.includes, function(n,i) {
						if (i === false) {
							a = false;
							return false;
						}
					});
					if (a === true) {
						$.each(c, function(k,v) {
							lib  = v.split('.');
							path = lib[0];
							name = lib[1];
							
							// Create a new class instance
							core.implement(v, true);
						});
					} else {
						wait_inner();
					}
				}, 10)
			})();
		})();
	};
	
	/**
	 * Implement Module (Private)
	 */
	core._implement = function(n,i) {
		
		// Could not locate the module
		if (!core.module.hasOwnProperty(n)) {
			throw new ModuleNotFound(n);
		}
		
		// Module object / namespace
		module = new core.module[n]();
		nspace = n.split('.');
		
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
	
	// Return the global namespace
	return core;
})();