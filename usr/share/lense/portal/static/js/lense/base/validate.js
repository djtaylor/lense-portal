/**
 * Lense Validator
 * 
 * Library of methods used to validate different types of data, mainly for forms.
 */
lense.import('LenseBaseValidate', function() {
	
	/**
	 * Python Module Path
	 */
	this.pymod = function(m) {
		mod_test = /^[a-zA-Z][a-zA-Z\.]*[a-zA-Z]$/;
		return (m.match(mod_test)) ? true : false;
	}
	
	/**
	 * Match Field
	 */
	this.match = function(v,f) {
		return (v == $(f).val()) ? true : false;
	}
	
	/**
	 * Password
	 */
	this.password = function(p) {
		pw_test = /^\S*(?=\S{8,})(?=\S*[a-z])(?=\S*[A-Z])(?=\S*[\d])(?=\S*[\W])\S*$/;
		return (p.match(pw_test)) ? true : false;
	}
	
	/**
	 * Validate Formula Name
	 */
	this.formula_name = function(i) {
		var fid_test = /^[a-z][a-z0-9\._]{3,}[a-z0-9]$/;
		return (i.match(fid_test)) ? true : false;
	}
	
	/**
	 * Validate Formula Label
	 */
	this.formula_label = function(n) {
		var fname_test = /^[a-zA-Z][a-zA-Z0-9 ]{3,}[a-zA-Z0-9]$/;
		return (n.match(fname_test)) ? true : false;
	}
	
	/**
	 * Validate Formula Description
	 */
	this.formula_desc = function(d) {
		var fdesc_test = /^[a-zA-Z][a-zA-Z0-9','\.-\s]{3,}[a-zA-Z0-9\.]$/;
		return (d.match(fdesc_test)) ? true : false;
	}
	
	/**
	 * Validate IPv4 Address
	 * 
	 * lense.validate.ip(4, '192.168.213.56');
	 */
	this.ipv4 = function(a) {
		var ipv4_test = /^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$/; 
		return (a.match(ipv4_test) || a == 'localhost') ? true : false;
	}
	
	/**
	 * Validate IPv6 Address
	 */
	this.ipv6 = function(a) {
		var ipv6_test = /^((?=.*::)(?!.*::.+::)(::)?([\dA-F]{1,4}:(:|\b)|){5}|([\dA-F]{1,4}:){6})((([\dA-F]{1,4}((?!\3)::|:\b|$))|(?!\2\3)){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})$/i;
		return (a.match(ipv6_test) || a == 'localhost') ? true : false;
	}
	
	/**
	 * Validate Integer
	 */
	this.int = function(i) {
		return (/^[\d]+$/.test(i)) ? true : false;
	}
	
	/**
	 * Validate Port
	 */
	this.port = function(p) {
		if (/^\d+$/.test(p)) {
			if (v > 0 && v < 65536) { return true; } 
			else { return false; }
		} else { return false; }
	}
	
	/**
	 * Validate Email Address
	 */
	this.email = function(e) {
		email_test = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
		return (e.match(email_test)) ? true : false;
	}
});