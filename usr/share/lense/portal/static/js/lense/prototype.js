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