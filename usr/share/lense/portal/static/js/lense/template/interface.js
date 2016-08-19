lense.import('template.interface', function() {
	var self = this;

	/**
	 * Compile a Handlebars template.
   *
   * @param {String} id The template ID
   * @param {Object} data Any template data
	 * @param {Object} opts Any additional options
	 */
	this.compile = function(id, data, opts) {
		var compiler = this;
		var compiled = Handlebars.compile($('#' + id).html())(data);

		/**
		 * Return compiled HTML
		 */
		this.html = function() {
			return compiled
		}

		// Return the compiler object
		return compiler
	}
});
