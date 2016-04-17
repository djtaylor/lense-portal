lense.import('common.url', function() {
	
	/**
	 * Redirect
	 */
	this.redirect = function(path) {
		window.location.replace('/' + path);
	}
	
	/**
	 * Parse URL
	 * 
	 * This method is used to render alert messages passed in the URL, and then cleans
	 * up the URL afterwards. Looks for 'status' and 'body' URL parameters.
	 */
	this.parse = function() {
		
		// Define persistent and notification URL parameters
		var url_objects = {
			"persistent": [ 'panel', 'edit'],
			"notify":     [ 'status', 'body' ]
		};
		
		// Check if the status and msg parameters are both set and render the message
		var status_val = lense.common.url.param_get('status');
		var msg_val    = lense.common.url.param_get('body');
		if (status_val !== null && msg_val !== null) {
			lense.common.layout.render(status_val, msg_val)
		}
		
		// Object notification parameters
		url_objects.notify.forEach(function(notify) {
			var notify_param = lense.common.url.param_get(notify);
			if (notify_param !== null) {
				var current_url = window.location.pathname;
				var base_url    = window.location.href.match(/^[^\#\?]+/)[0];
				var base_sep	= '?'
				var new_url     = base_url;
				url_objects.persistent.forEach(function(param_type) {
					var param_val = lense.common.url.param_get(param_type);
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
	 * Get URL Parameters
	 * 
	 * Helper method used to retrieve the value of a specific query parameter from the
	 * current URL.
	 * 
	 * @param {name} The name of the query parameter to retrieve the value of
	 */
	this.param_get = function(name) {
		return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
	}
	
});