class Utils {

	/**
	 * Clone Data
	 *
	 * Clone a variable by parsing and stringifying the value to prevent modification
	 * by reference. Creates a completely independent copy.
	 *
	 * @param {Object} data The data to copy
	 */
	static clone(data) {
		return JSON.parse(JSON.stringify(data));
	}

	/**
	 * Extend Object
	 *
	 * @param {Object} a The source object
	 * @param {Object} b The object to extend with
	 */
	static extend(a,b) {
		$.each(b, function(k,o) {
			if (hasattr(a, k)) {
				return true;
			}
			a[k] = b[k];
		});
		return a;
	}

	/**
	 * Variable Type Check
	 *
	 * @param {Object} obj The object to check
	 * @param {String} type The type to check
	 */
	static istype(obj, type) {
		switch(type) {
			case 'string':
			case 'str':
				return (typeof(obj) == 'string') ? true:false;
			case 'array':
			case 'list':
				return $.isArray(obj);
			case 'object':
			case 'dict':
			  return (obj.constructor == Object) ? true:false;
			case 'boolean':
			case 'bool':
			  return (typeof(obj) == 'boolean') ? true:false;
			case 'int':
			case 'integer':
			case 'num':
			case 'number':
			  return (typeof(obj) == 'number') ? true:false;
			default:
				return false;
		}
	}

	/**
	 * Extract Keys
	 *
	 * Extract a subset of keys from an object and return a new object.
	 *
	 * @param {Object} object The object to extract from
	 * @param {Array} keys The keys to extract
	 */
	static extract(object, keys) {
 		var _object = {};
 		$.each(keys, function(i,k) {
 			_object[k] = object[k];
 		});
 		return _object;
 	}

	/**
	 * Defined Check
	 *
	 * @param {*} v The data to check
	 */
	static defined(v) {
		if (v === null || v === undefined || v === false || v == '' || v == {} || v == []) {
			return false;
		} else { return true; }
	}

	/**
	 * Object Attribute Check
	 *
	 * @param {Object} obj The object to check against
	 * @param {String} key The key to check for
	 */
	static hasattr(obj, key) {
 		if (!defined(obj)) {
 			return false;
 		}

 		// jQuery object
 		if (obj instanceof jQuery) {
 			attrs = {};
 			if (obj.hasOwnProperty('target')) {
 				$.each(obj.target.attributes, function(key, a) {
 					attrs[a.nodeName] = a.value;
 				});
 			} else {
 				$.each(obj[0].attributes, function(key, a) {
 					attrs[a.nodeName] = a.value;
 				});
 			}
 			return hasattr(attrs, key);

 		// Javascript object
 		} else {
 			return obj.hasOwnProperty(key);
 		}
 	}

	/**
	 * Get Object Attribute
	 *
	 * @param {Object} obj The object to extract from
	 * @param {String} key The key to extract
	 * @param {*} def The default value
	 */
	static getattr(obj, key = undefined, def = undefined) {

		// No key provided
		if !Utils.defined(key) {
			attrs = {};
			if (e.hasOwnProperty('target')) {
				$.each(e.target.attributes, function(key, a) {
					attrs[a.nodeName] = a.value;
				});
			} else if (e.hasOwnProperty('attributes')) {
				$.each(e.attributes, function(key, a) {
					attrs[a.nodeName] = a.value;
				});
			} else {
				$.each($(e)[0].attributes, function(key, a) {
					attrs[a.nodeName] = a.value;
				});
			}
			return attrs;

		} else {

			// jQuery object
	 		if (obj instanceof jQuery) {
	 			attrs = {};
	 			if (obj.hasOwnProperty('target')) {
	 				$.each(obj.target.attributes, function(key, a) {
	 					attrs[a.nodeName] = a.value;
	 				});
	 			} else {
	 				$.each(obj[0].attributes, function(key, a) {
	 					attrs[a.nodeName] = a.value;
	 				});
	 			}
	 			return Utils.getattr(attrs, key, def);

	 		// JavaScript object
	 		} else {
	 			if (hasattr(obj, key)) {
	 				return obj[key];
	 			} else {
	 				if (def === undefined) {
	 					throw new Error("Object has no key '" + key + "', and no default provided!")
	 				}
	 				return def;
	 			}
	 		}
		}
 	}

	/**
	 * URL Manipulation
	 */
	class URL {

		/**
		 * Redirect
		 *
		 * @param {String} path The path to redirect to
		 */
		static redirect(path) {
			window.location.replace('/' + path);
		}

		/**
		 * Parse URL
		 */
		static parse() {

			// Define persistent and notification URL parameters
			var url_objects = {
				"persistent": [ 'view', 'edit', 'create', 'uuid'],
				"notify":     [ 'status', 'body' ]
			};

			// Object notification parameters
			url_objects.notify.forEach(function(notify) {
				var notify_param = URL.param_get(notify);
				if (notify_param !== null) {
					var current_url = window.location.pathname;
					var base_url    = window.location.href.match(/^[^\#\?]+/)[0];
					var base_sep	= '?'
					var new_url     = base_url;
					url_objects.persistent.forEach(function(param_type) {
						var param_val = URL.param_get(param_type);
						if (param_val !== null) {
							new_url = new_url + base_sep + param_type + '=' + param_val;
						}
						base_sep = '&';
					});
					history.pushState(null, null, new_url);
				}
			});
		}

		/**
		 * Set URL Parameters
		 *
		 * Helper method used to set new query parameters in the current URL.
		 *
		 * @param {key} The query parameter key
		 * @param {value} The query parameter value
		 */
		static param_set(key, value) {
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
		 * Delete URL Parameters
		 *
		 * Helper method used to remove a query parameter from the current URL before pushing
		 * the new history state.
		 *
		 * @param {key} The URL query parameter to remove
		 */
		static param_del(key) {
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
		 * Check URL Parameter Existence
		 */
		static param_exists(key) {
			var re = new RegExp('[&\?]{1}' + key, 'g');
			return (window.location.search.match(re)) ? true : false;
		}

		/**
		 * Get URL parameter
		 *
		 * @param {String} name The name of the query parameter to retrieve the value of
		 * @param {Mixed} def The default value if no attribute found
		 */
		static param_get(name, def) {
			return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||(defined(def) ? def:null);
		}
	}
}
