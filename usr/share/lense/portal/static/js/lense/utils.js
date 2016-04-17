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