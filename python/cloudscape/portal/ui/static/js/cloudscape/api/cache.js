/**
 * API Cache
 * 
 * Store cached data from API requests to re-use in other JavaScript classes
 * and methods.
 */
cs.import('CSAPICache', function() {
	
	// Cache containers
	this.hosts     = [];
	this.hgroups   = [];
	this.groups    = [];
	this.acls      = [];
	this.formulas  = [];
	this.endpoints = [];
	
	/**
	 * Callback: Cache Endpoints
	 */
	cs.register.callback('api.cache_endpoints', function(c,m,d,a) {
		if (cs.api.client.params.is_admin === true) {
			cs.api.cache.endpoints = m;
		}
	});
	
	/**
	 * Callback: Cache Formulas
	 */
	cs.register.callback('api.cache_formulas', function(c,m,d,a) {
		cs.api.cache.formulas = m;
	});
	
	/**
	 * Callback: Cache ACLs
	 */
	cs.register.callback('api.cache_acls', function(c,m,d,a) {
		if (cs.api.client.params.is_admin === true) {
			cs.api.cache.acls = m;
		}
	});
	
	/**
	 * Callback: Cache Host Groups
	 */
	cs.register.callback('api.cache_hgroups', function(c,m,d,a) {
		cs.api.cache.hgroups = m;
	});
	
	/**
	 * Callback: Cache Hosts
	 */
	cs.register.callback('api.cache_host', function(c,m,d,a) {
		cs.api.cache.hosts = m;
	});
	
	/**
	 * Callback: Cache Groups
	 */
	cs.register.callback('api.cache_group', function(c,m,d,a) {
		cs.api.cache.groups = m;
	});
	
	/**
	 * Get Cached Data
	 * 
	 * Helper object which contains method used to retrieve and filter through the cached
	 * API response objects.
	 */
	this.get = {
			
		/**
		 * ACLs
		 */
		acl: {
			
			/**
			 * Get Object ACLs
			 * 
			 * Filter out ACLs by object type and return an object organized using the
			 * ACL name as the key. If no type supplied, return all object ACLs.
			 * 
			 * @param {t} Object type
			 */
			object: function(t) {
				ret = {};
				$.each(cs.api.cache.acls, function(i,o) {
					if (o.type_object === true) {
						if (defined(t)) {
							if ($.inArray(o.name, ret) == -1) {
								ret[o.name] = {
									name: o.name,
									desc: o.desc,
									endpoints: []
								};
							}
							$.each(o.endpoints.object, function(_i,e) {
								ep = cs.api.cache.get.endpoints({uuid:e.endpoint_id});
								if (defined(ep) && ep['object'] == t) {
									ret[o.name].endpoints.push(ep);
								}
							});
							
						} else {
							ret[o.name] = o;
						}
					}
				});
				retp = {};
				$.each(ret, function(n,o) {
					if (!$.isEmptyObject(o.endpoints)) {
						retp[n] = o;
					}	
				});
				return retp;
			},
			
			/**
			 * Get Global ACLs
			 * 
			 * Return a constructed object of global ACLs organized using the ACL name as
			 * the key. Can supply an alternate key for sorting.
			 */
			global: function(k) {
				ret = {};
				$.each(cs.api.cache.acls, function(i,o) {
					if (o.type_global) {
						if (defined(k) && o.hasOwnProperty(k)) {
							ret[o[k]] = o;
						} else {
							ret[o.name] = o;
						}
					}
				});
				return ret;
			},
			
			/**
			 * Get Host ACLs
			 * 
			 * Return a constructed object of host ACLs organized using the ACL name as the
			 * key. Host ACLs are used when agent software on a managed host makes an API request.
			 */
			host: function() {
				ret = {};
				if (cs.api.cache.acls.hasOwnProperty('host')) {
					$.each(cs.api.cache.acls.host.defs, function(i,o) {
						ret[o.name] = o;
					});
				}
				return ret;
			}
		},
			
		/**
		 * Endpoints
		 */
		endpoints: function(e) {
			var ea = clone(cs.api.cache.endpoints);
			var ef = [];
			$.each(ea, function(i,_e) {
				var a = true;
				$.each(e, function(k,v) {
					if (!_e.hasOwnProperty(k) || _e[k] !== v) {
						a = false;
					}
				});
				if (a === true) {
					ef.push(_e);
				}
			});
			return (ef.length > 1) ? ef : ef[0];
		},
		
		/**
		 * Formulas
		 */
		formula: function(f) {
			var fa = clone(cs.api.cache.formulas);
			var ff = [];
			$.each(fa, function(i,_f) {
				var a = true;
				$.each(f, function(k,v) {
					if (!_f.hasOwnProperty(k) || _f[k] !== v) {
						a = false;
					}
				});
				if (a === true) {
					ff.push(_f);
				}
			});
			return (ff.length > 1) ? ff : ff[0];
		},
		
		/**
		 * Host Groups
		 */	
		hgroup: function(f) {
			var ha = clone(cs.api.cache.hgroups);
			var hf = [];
			$.each(ha, function(i,h) {
				var a = true;
				$.each(f, function(k,v) {
					if (!h.hasOwnProperty(k) || h[k] !== v) {
						a = false;
					}
				});
				if (a === true) {
					hf.push(h);
				}
			});
			return (hf.length > 1) ? hf : hf[0];
		},
		
		/**
		 * Hosts
		 */	
		host: function(f) {
			var ha = clone(cs.api.cache.hosts);
			var hf = [];
			$.each(ha, function(i,h) {
				var a = true;
				$.each(f, function(k,v) {
					if (!h.hasOwnProperty(k) || h[k] !== v) {
						a = false;
					}
				});
				if (a === true) {
					hf.push(h);
				}
			});
			return (hf.length > 1) ? hf : hf[0];
		}
	}
	
	/**
	 * ACL UUID to Name
	 */
	this.acl_uuid2name = function(a) {
		var name = undefined;
		$.each(cs.api.cache.acls, function(i,o) {
			if (o.uuid == a) {
				name = o.name;
				return false;
			}
		});
		return name;
	}
	
	/**
	 * Host Group UUID to Name
	 * 
	 * Map a host group UUID to its relative name using the cached API data.
	 * 
	 * @param {u} The host group UUID to map
	 */
	this.hgroup_uuid2name = function(u) {
		var name = undefined;
		$.each(cs.api.cache.hgroups, function(i,o) {
			if (o.uuid == u) {
				name = o.name;
				return false;
			}
		});
		return name;
	}
	
	/**
	 * Host UUID to Name
	 * 
	 * Map a host UUID to its relative name using the cached API data.
	 * 
	 * @param {u} The host UUID to map
	 */
	this.host_uuid2name = function(u) {
		var name = undefined;
		$.each(cs.api.cache.hosts, function(i,o) {
			if (o.uuid == u) {
				name = o.name;
				return false;
			}
		});
		return name;
	}
	
	/**
	 * Host Name to UUID
	 * 
	 * Map a host name to its relative UUID using the cached API data.
	 * 
	 * @param {n} The host name to map
	 */
	this.host_name2uuid = function(n) {
		var uuid = undefined;
		$.each(cs.api.cache.hosts, function(i,o) {
			if (o.name == n) {
				uuid = o.uuid;
				return false;
			}
		});
		return uuid;
	}
	
	/**
	 * Cache API Data
	 */
	this.construct = function() {
		
		// Endpoints
		cs.api.request.get({
			path:     'auth/endpoints',
			action:   'get',
			callback: {
				id: 'api.cache_endpoints'
			}
		});
		
		// Formulas
		cs.api.request.get({
			path:     'formula',
			action:   'get',
			callback: {
				id: 'api.cache_formulas'
			}
		});
		
		// ACLs
		cs.api.request.get({
			path:     'auth/acl',
			action:   'get',
			callback: {
				id: 'api.cache_acls'
			}
		});
		
		// Host Groups
		cs.api.request.get({
			path:     'host/group',
			action:   'get',
			callback: {
				id: 'api.cache_hgroups'
			}
		});
		
		// Hosts
		cs.api.request.get({
			path:     'host',
			action:   'get',
			callback: {
				id: 'api.cache_host'
			}
		});
		
		// Groups
		cs.api.request.get({
			path:     'group',
			action:   'get',
			callback: {
				id: 'api.cache_group'
			}
		});
	}
});