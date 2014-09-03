cs.import('CSFormulaInterface', function() {
	
	/**
	 * Initialize CSFormulaInterface
	 * @constructor
	 */
	this.__init__ = function() {
	
		// Formulas Overview
		if (cs.url.param_get('panel') == 'overview') {
			cs.implement('CSFormulaOverview', 'formula');
		}
		
		// Formula Details
		if (cs.url.param_get('panel') == 'details') {
			cs.implement('CSFormulaDetails', 'formula.editor');
		}
		
		// Formula Run
		if (cs.url.param_get('panel') == 'run') {
			cs.implement('CSFormulaRun', 'formula.run');
		}
	}
});