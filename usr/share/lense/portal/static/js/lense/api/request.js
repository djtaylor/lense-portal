/**
 * API Request
 * 
 * Object designed to handle submitting API request to the Lense
 * Socket.IO proxy server.
 */
lense.import('api.request', function() {
	
	/**
	 * Request Attributes
	 */
	this.attrs = {
		'user/create': {
			'msg': 'Creating user account...'
		},
		'group/create': {
			'msg': 'Creating group...'
		},
		'group/delete': {
			'msg': 'Deleting group...'
		},
		'group/update': {
			'msg': 'Updating group attributes...'
		},
		'group/member/add': {
			'msg': 'Adding member to group...'
		},
		'group/member/remove': {
			'msg': 'Removing member from group...'
		},
		'utility/create': {
			'msg': 'Creating new utility...'
		},
		'utility/delete': {
			'msg': 'Deleting utility definition...'
		},
		'acl/create': {
			'msg': 'Creating new ACL...'
		}
	};
	
	/**
	 * Method: API Submit
	 * 
	 * @param {f} The form identifier string, i.e. 'add_host'
	 */
	lense.common.register.method('api.submit', function(f) {
		
		// Helper method to convert slash delimited parameter paths
		function _csp(p,v,o) {
			function _csp_inner(_p,_o) {
				if (_p.length == 1) {
					_o[_p[0]] = v;
				} else {
					if (!_o.hasOwnProperty(_p[0])) {
						_o[_p[0]] = {};
					}
					_k = _p[0];
					_p.shift();
					_csp_inner(_p,_o[_k]);
				}
			}
			if (p.indexOf('/') > -1) {
				_csp_inner(p.split('/'), o);
			} else {
				o[p] = v;
			}
		}
		
		// Internal request attributes and parameters
		var ia = ['action', 'path', 'method', 'callback'];
		var ip = {}
		
		// API attributes key
		var ak = null;
		
		// Validate the form fields
		field_check = lense.common.forms.validate('#' + f);
		if (field_check === true) {
			
			// Construct the JSON request data
			json_data = {};
			$.each(lense.common.forms.all[f]['inputs'], function(key, obj) {
				
				// Internal request attributes
				if ($.inArray(obj.name, ia) > -1) {
					ip[obj.name] = obj.value;
					
				// Request data
				} else {
					
					// If ignoring this field
					if (obj.hasOwnProperty('ignore')) { return true; }
					
					// If using an alterate data mapping
					dmap = obj.name;
					if (obj.hasOwnProperty('data_map')) {
						dmap = obj.data_map;
					}
					
					// If parsing into a JSON object
					if (obj.hasOwnProperty('parse')) {
						
						// Parse a comma seperated list
						if (obj.parse == 'list') {
							if (!defined(obj.value)) {
								obj.value = [];
							} else {
								obj.value = obj.value.split(',');
							}
						}
					}
					
					// If processing a checkbox
					if (obj.type == 'checkbox') {
						if (!$('input[type$="checkbox"][form$="' + f + '"][name$="' + obj.name + '"]').is(':checked')) {
							if (obj.value.indexOf('bool:') >= 0) {
								_csp(dmap, false, json_data);
								return true;
							} else {
								return true;
							}
						}
					}
					
					// Extract bool values, i.e. 'value="bool:true"'
					if (obj.value.indexOf('bool:') >= 0) {
						bp = obj.value.split(':');
						_csp(dmap, (bp[1] === 'true') ? true : false, json_data);
					
					// Extract values from hidden fields
					} else if (obj.value.indexOf('input:') >= 0) {
						fp = obj.value.split(':');
						_csp(dmap, $('input' + fp[1]).val(), json_data);
						
					// Extract global values, i.e. 'value="global:attr_name"'
					} else if (obj.value.indexOf('global:') >= 0) {
						gp = obj.value.split(':');
						_csp(dmap, cs_global[gp[1]], json_data);
					
					// Extract default values
					} else {
						_csp(dmap, obj.value, json_data);
					}
				}
			});
			
			// Set the attributes key
			ak = ip.path + '/' + ip.action;
			
			// Process any API data filters
			json_data = lense.common.forms.filter(f, 'api_data', json_data);
			
			// Clear the form
			$.each(lense.common.forms.all[f]['inputs'], function(key, obj) {
				if (!obj.hasOwnProperty('noreset')) {
					$('input[form$="' + f + '"][name$="' + obj.name + '"]').val(null);
					$('div[type$="icon"][form$="' + f + '"][name$="' + obj.name + '"]').replaceWith('<div class="form_input_icon_def" type="icon" form="' + f + '" name="' + obj.name + '"></div>');
				}
			});
			
			// Submit the API request
			lense.common.layout.popup_toggle(false, false, false, function() {
				lense.common.layout.loading(true, lense.api.request.attrs[ak].msg, function() {
					
					// Construct the request parameters
					rp = {
						path:   ip.path,
						action: ip.action,
						_data:  json_data
					};
					
					// If using a callback method
					if (ip.hasOwnProperty('callback')) {
						rp.callback = { id: ip.callback }
					}
					
					// Submit the API request
					lense.api.request.submit(ip.method, rp);
				});
			});
			
		// Form is invalid
		} else {
			lense.common.layout.show_response(true, { tgt: f, msg: 'Please fill in the required fields...' }, function() {
				$.each(lense.common.forms.all[f]['inputs'], function(key, obj) {
					if (obj.hasOwnProperty('required') && !defined(obj.value)) {
						lense.common.forms.set_input(obj._parent, obj.name, undefined);
					}
				});
			});
		}
	});
	
	/**
	 * API GET
	 * 
	 * Wrapper method used to submit a GET request via the API proxy server.
	 * 
	 * @param {a} The request parameters
	 */
	this.get = function(p) {
		lense.api.request.submit('get',p);
	}
	
	/**
	 * API POST
	 * 
	 * Wrapper method used to submit a POST request via the API proxy server.
	 * 
	 * @param {a} The request parameters
	 */
	this.post = function(p) {
		lense.api.request.submit('post',p);
	}
	
	/**
	 * API PUT
	 * 
	 * Wrapper method used to submit a PUT request via the API proxy server.
	 * 
	 * @param {a} The request parameters
	 */
	this.put = function(p) {
		lense.api.request.submit('put',p);
	}
	
	/**
	 * API DELETE
	 * 
	 * Wrapper method used to submit a DELETE request via the API proxy server.
	 * 
	 * @param {a} The request parameters
	 */
	this.del = function(p) {
		lense.api.request.submit('delete',p);
	}
	
	/**
	 * Submit API Request
	 * 
	 * Handler method for submitting API requests via Socket.IO.
	 * 
	 * @param {m} The request method
	 * @param {p} The request parameters
	 */
	this.submit = function(m,p) {
		
		// Construct the request object
		request = {
			'auth': {
				'user':   lense.api.client.params.user,
				'token':  lense.api.client.params.token,
				'group':  lense.api.client.params.group,
			},
			'socket': {
				'method': m,
				'path':   p.path,
				'room':   lense.api.client.room,
			}
		}
		
		// If request data is supplied
		if (defined(p._data)) { 
			request['_data'] = p._data; 
		}
		
		// If a callback object is specified
		if (defined(p.callback)) { 
			request['socket']['callback'] = p.callback; 
		}
		
		// Valid request method
		vm = $.inArray(request.socket.method, ['get', 'post']) > -1;
		
		// If the method is valid
		if (vm) {
			lense.api.client.io.emit('submit', request)
		} else { return false; }
	}
});