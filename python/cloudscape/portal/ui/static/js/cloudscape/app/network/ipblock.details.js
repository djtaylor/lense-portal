cs.import('CSNetworkIPBlockDetails', function() { 
	
	// Active Block / Protocol
	this.active = cs.url.param_get('block');
	this.proto  = $('input[type="hidden"][name="protocol"]').val();
	
});