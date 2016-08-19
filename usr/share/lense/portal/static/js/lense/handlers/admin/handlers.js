lense.import('admin.handlers', function() { 
	var self = this;
	
	/**
	 * Load Handlers Callback
	 */
	lense.register.callback('loadHandlers', function(data) {
		var parents   = ['#handlers_list_body', '#handlers_thumbnails'];
		var templates = ['object_row', 'object_thumbnail'];
		
		// Render handlers
		lense.common.template.render(parents, templates, data, {
			callback: waitingDialog.hide,
			display: ['path', 'method', 'protected', 'enabled'],
			title: 'name',
			headers: '#handlers_list_headers'
		});
	});
	
	/**
	 * Load Handler Details Callback
	 */
	lense.register.callback('loadHandlerDetails', function(data) {
		lense.common.template.render('#handler_properties_container', 'handler_properties', data, {
			callback: function() {
				lense.common.ace.setup('manifests-editor', {
					data: data.manifest
				});
				waitingDialog.hide();
			}
		});
	});
	
	/**
	 * Constructor
	 */
	lense.register.constructor('admin.handlers', function() {
		
		// Load handler details
		if (url.param_exists('uuid')) {
			waitingDialog.show('Loading handler: ' + url.param_get('uuid'));
			lense.common.layout.fadein('#handlers_detail', function() {
				lense.api.request.submit('handler_get', { 'uuid': url.param_get('uuid') }, 'loadHandlerDetails');
			});
			
		// Load handlers list
		} else {
			waitingDialog.show('Loading handlers...');
			lense.common.layout.fadein('#handlers_overview', function() {
				lense.api.request.submit('handler_get', null, 'loadHandlers');
			});
			
			// Create handler modal
			try {
				self.createModal();
			} catch(e) {
				console.log(e);
			}
		}
	});
	
	/**
	 * Create Handler Modal
	 */
	this.createModal = function() {
		lense.common.template.render('#create-object-modal', 'object_create', {
			type: 'handler',
			attrs: ['name','desc','path','method','protected','manifest'],
			handler: 'handler_create',
			object: 'handler',
			callback: 'createHandler',
			fields: [
			    {
			    	type: 'text',
			    	name: 'name',
			    	required: true,
			    	label: 'Name'
			    },
			    {
			    	type: 'text',
			    	name: 'desc',
			    	required: true,
			    	label: 'Description'
			    },
			    {
			    	type: 'text',
			    	name: 'path',
			    	required: true,
			    	label: 'Path'
			    },
			    {
			    	type: 'select',
			    	name: 'method',
			    	options: ['GET', 'POST', 'PUT', 'DELETE'],
			    	label: 'Method'
			    },
			    {
			    	type: 'select',
			    	name: 'protected',
			    	selected: 'Yes',
			    	options: {'Yes': 'true', 'No': 'false'},
			    	label: 'Protected'
			    },
			    {
			    	type: 'textarea',
			    	name: 'manifest',
			    	label: 'Manifest'
			    }
			]
		});
	}
});