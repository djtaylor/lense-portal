lense.import('Common', function() {
	this.__init__ = function() {	
		$("#ui ul").gridster({
			widget_margins: [10, 10],
			widget_base_dimensions: [140, 140]
		});
	}
});