/**
 * String Prototype Methods
 */

// String Contains
String.prototype.contains = function(str, index) {
	return (this.indexOf(str, index) !== -1) ? true : false;
}

// String Starts With
String.prototype.startswith = function(str) {
	return (this.substring(0, str.length) === str) ? true : false;
}

// String Ends With
String.prototype.endswith = function(str) {
	return (this.indexOf(str, this.length - str.length) !== -1) ? true: false;
}

/**
 * Array Prototype Methods
 */

// Array Contains
Object.defineProperty(Array.prototype, 'contains', {
	value: function(str) {
		return (this.indexOf(str) !== -1) ? true: false;
	}
});

/**
 * Ordered object protoype
 *
 * @param {Array} orderedData An array of object elements
 * @returns {OrderedObject}
 */
function OrderedObject(orderedData) {
	var self  = this;
	self.data = (defined(orderedData) ? orderedData:[]);

	// orderedData must be an array
	if (!istype(self.data, 'array')) {
		lense.raise('Ordered data object must be constructed with an Array!');
	}

	// Check the list format
	$.each(self.data, function(i,obj) {
		if (!istype(obj, 'array') || !obj.length === 2 || !istype(obj[0], 'str')) {
			lense.raise('Ordered data [' + i + '] must be an array of arrays: \'[ ["key1", obj1],["key2", obj2] ]\'!');
		}
	});

	/**
	 * Return a hash of the ordered object (sorting lost)
	 *
	 * @return {Object}
	 */
	self.hash = function() {
		var hash = {};
		self.each(function(k,obj) {
			hash[k] = obj;
		});
		return hash;
	}

	/**
	 * Retrieve object by key
	 *
	 * @param {String} key The key to find
	 * @param {Object} opts Any additional options
	 * @returns {*}
	 */
	self.get = function(key, def) {
		var retval = def;
		$.each(self.data, function(i,obj) {
			if (obj[0] === key) {
				retval = obj[1];
			}
		});
		return retval;
	}

	/**
	 * Delete object by key
	 *
	 * @param {String} key The key to delete
	 */
	self.del = function(key) {
		$.each(self.data, function(i,obj) {
			if (obj[0] === key) {
				self.data.splice(i, 1);
				return false;
			}
		});
	}

	/**
	 * Iterate through object
	 *
	 * @param {Function} callback A callback function
	 * @returns {Function}
	 */
	self.each = function(callback) {
		$.each(self.data, function(i, obj) {
			return callback(obj[0], obj[1]);
		});
	}

	/**
	 * Append new element to ordered object
	 *
	 * @param {String} key The element key
	 * @param {*} value The element value
	 */
	self.append = function(key, value) {
		self.data.push([ key, value ]);
	}
}
