var cs = (function() {
	var self = {};
	
	// Modules container
	self.module   = {};
	
	// Includes container
	self.includes = {};
	
	/**
	 * Import Module
	 * 
	 * Import an included module into the CloudScape namespace. This assumes that the parent
	 * namespace has already been initialized.
	 * 
	 * @param {n} The name of the module
	 * @param {m} The module contents
	 */
	self.import = function(n,m) {
		self.module[n] = m;
	};
	
	/**
	 * Bootstrap Namespace
	 * 
	 * Bootstrap any objects found in the constructors argument using the internal 'implement'
	 * method.
	 * 
	 * @param {c} Class constructor definitions
	 */
	self.bootstrap = function(c) {
		
		// Wait for all includes to complete
		(function() {
			$.each(self.includes, function(n,i) {
				(function wait_inner(n) {
					setTimeout(function() {
						if (!self.module.hasOwnProperty(n)) {
							wait_inner(n);
						} else {
							self.includes[n] = true;
						}
					}, 10);
				})(n);
			});
			
			// All included
			return true;
		})();
		
		console.log('All includes complete');
		console.log(self.includes);
		
		// Bootstrap after includes completed
		(function() {
			(function wait_inner() {
				setTimeout(function() {
					var a = true;
					$.each(self.includes, function(n,i) {
						if (i === false) {
							a = false;
							return false;
						}
					});
					if (a === true) {
						for (var m in c) {
							lib  = c[m].split('.');
							path = lib[0];
							name = lib[1];
							
							console.log('Implementing ' + name + ' to path ' + path);
							
							// Create a new class instance
							self.implement(name, path);
						}
					} else {
						wait_inner();
					}
				}, 10)
			})();
		})();
	};
	
	/**
	 * Implement Module
	 * 
	 * Extend the current namespace with a new module object. Appends the module to the existing
	 * namespace with the path specified.
	 * 
	 * @param {n} The module name, should exist in the modules container
	 * @param {p} The module path, used to access internally
	 */
	self.implement = function(n,p) {
		function set_path(s,p,o) {
			function _inner(_s,_p,_o) {
				if (_p.length == 1) {
					_s[_p[0]] = _o;
				} else {
					_n = _p.shift()
					_inner(_s[_n],_p,_o);
				}
			}
			_inner(s,p.split('.'),o);
		}
		
		// Create a new child object
		if (self.module.hasOwnProperty(n)) {
			object = new self.module[n]();
		} else {
			throw new ModuleNotFound(n);
		}
		
		// Set the object in the namespace
		set_path(self,p,object);
		
		// Call the constructor if one exists
		(function() {
			if (object.hasOwnProperty('__init__')) {
				object.__init__();
			} else {
				object.__init__ = undefined;
			}
		}());
	};
	
	// Return the global namespace
	return self;
})();