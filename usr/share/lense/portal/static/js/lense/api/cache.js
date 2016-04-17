lense.import('api.cache', function() {
	
	// Cache containers
	this.groups   = [];
	this.acls     = [];
	this.handlers = [];
	
	/**
	 * Callback: Cache Handlers
	 */
	lense.common.register.callback('api.cache_handlers', function(c,m,d,a) {
		if (lense.api.client.params.is_admin === true) {
			lense.api.cache.handlers = m;
		}
	});
	
	/**
	 * Callback: Cache ACLs
	 */
	lense.common.register.callback('api.cache_acls', function(c,m,d,a) {
		if (lense.api.client.params.is_admin === true) {
			lense.api.cache.acls = m;
		}
	});
	
	/**
	 * Callback: Cache Groups
	 */
	lense.common.register.callback('api.cache_group', function(c,m,d,a) {
		lense.api.cache.groups = m;
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
				$.each(lense.api.cache.acls, function(i,o) {
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
								ep = lense.api.cache.get.endpoints({uuid:e.endpoint_id});
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
				$.each(lense.api.cache.acls, function(i,o) {
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
		},
			
		/**
		 * Handlers
		 */
		handlers: function(e) {
			var ea = clone(lense.api.cache.handlers);
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
		}
	}
	
	/**
	 * ACL UUID to Name
	 */
	this.acl_uuid2name = function(a) {
		var name = undefined;
		$.each(lense.api.cache.acls, function(i,o) {
			if (o.uuid == a) {
				name = o.name;
				return false;
			}
		});
		return name;
	}
	
	/**
	 * Cache API Data
	 */
	this.construct = function() {
		
		// Handlers
		lense.api.request.get({
			path:     'handler',
			callback: {
				id: 'api.cache_utilities'
			}
		});
		
		// ACLs
		lense.api.request.get({
			path:     'acl/keys',
			callback: {
				id: 'api.cache_acls'
			}
		});
		
		// Groups
		lense.api.request.get({
			path:     'group',
			callback: {
				id: 'api.cache_group'
			}
		});
	}
});