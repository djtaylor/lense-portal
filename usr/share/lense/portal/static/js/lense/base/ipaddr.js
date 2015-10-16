lense.import('LenseBaseIPAddr', function() {
	
	/**
	 * IPv4 Utilities
	 */
	this.v4 = {
		
		/**
		 * IP Number
		 */
		number: function(ip) {
			var ip_match = ip.match(/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/);
			return (ip_match) ? (+ip_match[1]<<24) + (+ip_match[2]<<16) + (+ip_match[3]<<8) + (+ip_match[4]) : null;
		},
		
		/**
		 * IP Mask
		 */
		mask: function(size) {
			return -1<<(32-size);
		},
			
		/**
		 * Private IP Test
		 */
		is_private: function(ip) {
			var reserved = {
		      '0.0.0.0': 8, 
		      '10.0.0.0': 8, 
		      '100.64.0.0': 10, 
		      '127.0.0.0': 8, 
		      '169.254.0.0': 16,
		      '172.16.0.0': 12, 
		      '192.0.0.0': 24, 
		      '192.0.2.0': 24,  
		      '192.88.99.0': 24, 
		      '192.168.0.0': 16, 
		      '198.18.0.0': 15, 
		      '198.51.100.0': 24, 
		      '203.0.113.0': 24,  
		      '224.0.0.0': 8, 
		      '225.0.0.0': 8, 
		      '226.0.0.0': 8, 
		      '227.0.0.0': 8, 
		      '228.0.0.0': 8, 
		      '229.0.0.0': 8, 
		      '230.0.0.0': 8, 
		      '231.0.0.0': 8, 
		      '232.0.0.0': 8, 
		      '233.0.0.0': 8, 
		      '234.0.0.0': 8, 
		      '235.0.0.0': 8, 
		      '236.0.0.0': 8, 
		      '237.0.0.0': 8, 
		      '238.0.0.0': 8, 
		      '239.0.0.0': 8, 
		      '255.255.255.255': 32, 
		    }; 
		    var results = $.map(reserved, function(m,i){ 
		      return (lense.ipaddr.v4.number(i) & lense.ipaddr.v4.mask(m)) == (lense.ipaddr.v4.number(ip) & lense.ipaddr.v4.mask(m)); 
		    });
		    return (results.indexOf(true) > 0) ? true : false;
		}
	}
	
	/**
	 * IPv6 Utilities
	 */
	this.v6 = {
		
	}
});