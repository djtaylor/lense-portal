lense.import('api.client', function() {
	var self = this;
	
	// Class attributes
	this.params, this.room, this.io;
	
	// Cookie keys
	this.cookies = ['user', 'group', 'key', 'token', 'endpoint', 'session'];
	
	/**
	 * Initialize APIClient
	 */
	this.__init__ = function() {
		
		// Parameters
		self.params = self.getParameters();
		self.room   = self.getRoom();
	}
	
	/**
	 * Get Client Parameters
	 */
	this.getParameters = function() {
		var _params = {};
		$.each(self.cookies, function(i,k) {
			_params[k] = Cookies.get(k);
		});
		return _params;
	}
	
	/**
	 * Get Client Room
	 */
	this.getRoom = function() {
		return self.params.user + ':' + self.params.session;
	}
	
	/**
	 * Emit SocketIO Message
	 * 
	 * @param {type}     The socket server request type
	 * @param {data}     Any additional socket data
	 * @param {callback} An optional callback method
	 */
	this.emit = function(type, data, callback) {
		var data = ((defined(data)) ? data : {});
		
		// Append room if required
		data['room'] = ((defined(data['room'])) ? data['room'] : self.room);
		
		// Emit the request
		self.io.emit(type, data);
		
		// Optional callback
		if (defined(callback)) {
			callback();
		}
	}
	
	/**
	 * Get Authentication Parameters
	 */
	this.authentication = function() {
		return {
			'user':   self.params.user,
			'token':  self.params.token,
			'group':  self.params.group,
		}
	}
	
	/**
	 * Open SocketIO Connection
	 */
	this.sockConnect = function(callback) {
		self.io = io.connect(self.params.endpoint);
		
		// Connection error
		self.io.on('error', function(e) {
			return lense.common.layout.notify('danger', 'IOConnect Error: ' + e);
		});
		
		// Connect failed
		self.io.on('connect_failed', function(e) {
			return lense.common.layout.notify('danger', 'IOConnect Failed: ' + e);
		});
		
		// Join client to room
		self.emit('join');
		
		// Join success
		self.io.on('joined', function(d) {
			lense.api.cache.handlers = d.handlers;
			lense.api.cache.server   = d.server;
			
			// Update client parameters
			$('input.socketio-server').val(lense.api.cache.server);
		});
		
		// Handle closed connections
		self.io.on('disconnect', function() {
			lense.api.setSockStatus('connecting');
		});
		
		// Run the callback
		if (defined(callback)) {
			callback();
		}
	}
});