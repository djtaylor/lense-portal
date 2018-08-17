lense.import('common.ace', function() {
	var self = this;
	
	// Editor objects
	this.editors = [];
	
	/**
	 * Retrieve Editor Object
	 */
	this.editor = function(id) {
		return self.editors[id];
	}
	
	/**
	 * Setup Manifest Editor
	 */
	this.setup = function(id, target, options) {
		
		// Target element
		self.editors[id] = ace.edit(target);
		
		// Theme / mode
		self.editors[id].setTheme(getattr(options, 'theme', 'ace/theme/chrome'));
		self.editors[id].getSession().setMode(getattr(options, 'mode', 'ace/mode/json'));
		
		// Read only
		self.editors[id].setReadOnly(getattr(options, 'readOnly', true));
		
		// Autosize editor window
		self.editors[id].$blockScrolling = Infinity;
		self.editors[id].setOptions({
			maxLines: Infinity
		});
		
		// If providing initial data
		if (hasattr(options, 'data') !== false) {
			self.editors[id].setValue(JSON.stringify(options.data, undefined, 2), -1);
		}
	}
});