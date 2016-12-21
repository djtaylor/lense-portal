/**
 * Clone Data
 *
 * Clone a variable by parsing and stringifying the value to prevent modification
 * by reference. Creates a completely independent copy.
 *
 * @param {d} The data to copy
 */
function clone(d) {
	return JSON.parse(JSON.stringify(d));
}

function extend(a,b) {
	var c = null;
	$.each(b, function(k,o) {
		if (hasattr(a, k)) {
			return true;
		}
		a[k] = b[k];
	});
	return c;
}

/**
 * Variable type check
 */
function istype(obj, type) {
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
 */
function extract(object, keys) {
	var _object = {};
	$.each(keys, function(i,k) {
		_object[k] = object[k];
	});
	return _object;
}

/**
 * Is a variable defined or not
 *
 * @param {*} v The value to check
 * @return {Boolean} defined
 */
function defined(v) {
	if (v === null || v === undefined || v === false || v == '' || v == {} || v == []) {
		return false;
	} else { return true; }
}

/**
 * Has Attribute Check
 */
function hasattr(obj, key) {
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
 */
function getattr(obj, key, def) {

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
		return getattr(attrs, key, def);

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

/**
 * Set Keyword Arguments
 */

/**
 * Get Element Attributes
 *
 * Takes an element object as an argument and returns an object containing attribute
 * names and values.
 *
 * @param {e} The element to retrieve attributes for
 */
function get_attr(e) {
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
}

/**
 * URL Manipulation
 */
var url = new function() {
	var self = this;

	/**
	 * Redirect
	 */
	this.redirect = function(path) {
		window.location.replace('/' + path);
	}

	/**
	 * Parse URL
	 */
	this.parse = function() {

		// Define persistent and notification URL parameters
		var url_objects = {
			"persistent": [ 'view', 'edit', 'create', 'uuid'],
			"notify":     [ 'status', 'body' ]
		};

		// Object notification parameters
		url_objects.notify.forEach(function(notify) {
			var notify_param = self.param_get(notify);
			if (notify_param !== null) {
				var current_url = window.location.pathname;
				var base_url    = window.location.href.match(/^[^\#\?]+/)[0];
				var base_sep	= '?'
				var new_url     = base_url;
				url_objects.persistent.forEach(function(param_type) {
					var param_val = self.param_get(param_type);
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
	this.param_set = function(key, value) {
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
	this.param_del = function(key) {
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
	this.param_exists = function(key) {
		var re = new RegExp('[&\?]{1}' + key, 'g');
		return (window.location.search.match(re)) ? true : false;
	}

	/**
	 * Get URL parameter
	 *
	 * @param {String} name The name of the query parameter to retrieve the value of
	 * @param {Mixed} def The default value if no attribute found
	 */
	this.param_get = function(name, def) {
		return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||(defined(def) ? def:null);
	}
}
