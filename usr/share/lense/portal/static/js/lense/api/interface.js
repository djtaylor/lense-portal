lense.import('api.interface', function() {
	var self    = this;

	// Socket status
	this.status = 'disconnected';

	/**
	 * Initialize APIInterface
	 * @constructor
	 */
	this.__init__ = function() {

		// Load modules
		lense.implement([
			'api.client',
			'api.request',
			'api.response',
			'api.cache',
		]);

		// Open the API connection
		self.connect();
	}

	/**
	 * Set Socket Information
	 *
	 * @param {connected} Is the socket connected or not
	 */
	this.setSockInfo = function(connected) {
		var endpoint = ((connected === true) ? lense.api.client.params.endpoint: '');
		var room     = ((connected === true) ? lense.api.client.room: '');
		var server   = ((connected === true) ? lense.api.cache.server: '');
		var status   = ((connected === true) ? 'connected': 'disconnected');

		// Update the client information
		$('input.socketio-endpoint').val(endpoint);
		$('input.socketio-room').val(room);
		$('input.socketio-server').val(server);

		// Store the socket status
		self.status = status;
	}

	/**
	 * Socket Status
	 *
	 * @param {status} The status string to update to
	 */
	this.setSockStatus = function(status) {
		switch(status) {

			// SocketIO disconnected
			case 'disconnected':
				$("#socketio-connected").css('display', 'none');
				$("#socketio-disconnected").css('display', 'all');
				$('#socketio-button').removeClass('active btn-success');
				$('#socketio-button').addClass('btn-default');

				// Clear client socket information
				self.setSockInfo(false);
				return true;

			// SocketIO connecting
			case 'connecting':
				$("#socketio-disconnected").css('display', 'none');
				$("#socketio-connected").css('display', 'none');
				$("#socketio-button").addClass('active btn-default');
				$('#socketio-button').removeClass('btn-success');
				return true;

			// SocketIO connected
			case 'connected':

				// Update button indicator
				$('#socketio-button').removeClass('active btn-default');
				$("#socketio-button").addClass('btn-success');
				$("#socketio-connected").css('display', 'all');
				$("#socketio-disconnected").css('display', 'none');

				// Set socket information
				self.setSockInfo(true);
				return true;

			// Invalid status
			default:
				return false;
		}
	}

	/**
	 * Open Socket<->API Connection
	 */
	this.connect = function() {

		// On page ready
		$(document).ready(function() {

			// Listen for responses / messages
			self.listen();

			// Build the cache
			lense.api.cache.construct();
		});
	}

	/**
	 * Response Listener
	 */
	this.listen = function() {

		// Update SocketIO indicator
		self.setSockStatus('connecting');

		// Open SocketIO connection
		lense.api.client.sockConnect(function() {

			// Response handler
			lense.api.client.io.on('connect', function() {
				self.setSockStatus('connected');

				// API response
				lense.api.client.io.on('apiResponse', function(response) {
					new lense.api.response.Object(response);
				});
			})
		});
	}
});
