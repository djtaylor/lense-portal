lense.import('api.cache', function() {
	var self      = this;

	// Cache containers
	this.users    = null;
	this.groups   = null;

	/**
	 * Cached Data Interface
	 *
	 * @param {String} type The object type
	 * @param {Object} data The object data
	 */
	function CachedDataInterface(type, data) {
		var inner  = this;

		// Object type / data
		inner.type = type;
		inner.data = data;

		/**
		 * Map Object
		 *
		 * @param {String} key The key string to map
		 * @param {String} value The key value to look for
		 * @param {String} attr The mapped attribute value to return
		 */
		inner.map = function(key, value, attr) {
			var retval = null;
			$.each(inner.data, function(i,obj) {
				if (hasattr(obj, key) && obj[key] == value) {
					retval = getattr(obj, attr, null);
				}
			});
			return retval;
		}
	}

	/**
	 * Callback for users data
	 */
	lense.register.callback('cachedUsers', function(data) {
		self.users = new CachedDataInterface('users', data);
	});

	/**
	 * Callback for groups data
	 */
	lense.register.callback('cachedGroups', function(data) {
		self.users = new CachedDataInterface('groups', data);
	});

	/**
	 * Construct Cache
	 */
	this.construct = function() {

		// Retrieve users and groups
		lense.api.request.submit('user_get', null, 'cachedUsers');
		lense.api.request.submit('group_get', null, 'cachedGroups');
	}
});
