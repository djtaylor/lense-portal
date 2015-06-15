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

/**
 * Definition Check
 * 
 * Simple helper method to check if a variable is defined or not. Checks
 * for null, undefined, false, or an empty string.
 * 
 * @param {v} The variable to check
 * @return bool
 */
function defined(v) {
	if (v === null || v === undefined || v === false || v == '' || v == {} || v == []) {
		return false;
	} else { return true; }
}

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
 * Include Module
 * 
 * Programatically include a JavaScript module.
 * 
 * @param {m} Either a single module or array of modules
 * @param {f} Optional filter attributes
 * @param {c} Callback
 */
function include(m,f,c) {
	var container = 'scripts';
	
	// URL attributes
	_url = {
		path:  function() {
			pathname = window.location.pathname.match(/^.*\/([^\/]*$)/);
			return ((defined(pathname)) && (1 in pathname)) ? pathname[1] : false;
		}(),
		panel: function() {
	    	search = window.location.search.match(/^.*panel=([^&]*).*$/);
			return ((defined(search)) && (1 in search)) ? search[1] : false;
		}()
	}
	
	// If performing any type of filtering
	if (defined(f)) {
	
		// If performing URL matching
		if (f.hasOwnProperty('url')) {
			for (var k in f.url) {
				if (f.url[k] instanceof Array) {
					if (f.url[k].indexOf(_url[k]) == -1) {
						return;
					}
				} else {
					
					// If performing a negative match
					if (f.url[k].startswith('!')) {
						p = f.url[k].replace('!', '');
						if (_url[k] == p) {
							return;
						}
					} else {
						if (_url[k] !== f.url[k]) {
							return;
						}
					}
				}
			}
		}
		
		// If performing administrator right checks
		if (f.hasOwnProperty('is_admin')) {
			if (!defined(api_params.is_admin)) {
				return;
			}
			if (h.is_admin === true) {
				if (api_params.is_admin !== true) {
					return;
				}
			}
		}
	}
	
	// Append the script to the page
	function append(f) {
		
		// Create the script container
		var div = document.createElement('script');
		div.setAttribute('type', 'text/javascript');
		div.setAttribute('src', '/static/js/cloudscape/' + f);
		
		// Get the parent container and prepend
		document.getElementById(container).appendChild(div);
	}
	
	// Include modules
	$.each(m, function(n,p) {
		cs.includes[n] = false;
		append(p);
	});
	
	// Run the callback
	if (defined(c)) {
		c();
	}
}