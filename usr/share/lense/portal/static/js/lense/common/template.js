lense.import('common.template', function() {
	var self = this;
	
	/**
	 * Constructor
	 * @constructor
	 */
	lense.register.constructor('common.template', function() {
		self.registerHelpers();
	});
	
	/**
	 * Register
	 */
	this.register = function(id) {
		
	}
	
	/**
	 * Register Helpers
	 */
	this.registerHelpers = function() {
		
		/**
		 * Widget Body
		 */
		Handlebars.registerHelper('widget_body', function(data, opts) {
			
		});
		
		/**
		 * Widget Object
		 */
		Handlebars.registerHelper('widget_object', function(widgetId, widgetType, widgetKey, widgetMap, opts) {
			widget_key   = ((defined(widgetKey)) ? ' widget-key="' + widgetKey + '"': '');
			widget_map   = ((defined(widgetMap)) ? ' widget-map="' + widgetMap + '"': '');
			widget_uuid  = lense.uuid4();
			widget_attrs = 'widget-id="' + widgetId + '" widget-type="' + widgetType + '" widget-uuid="' + widget_uuid + '"' + widget_key + widget_map;
			grid_attrs   = 'data-gs-width="12" data-gs-height="1" data-gs-auto-position="true" data-gs-no-resize="true" ';
			
			// Return the HTML object
			return new Handlebars.SafeString(
				'<div class="grid-stack-item" ' + grid_attrs + widget_attrs + '>' +
				'<x-var type="object">' +
				opts.fn(this) + '</x-var></div>');
		});
		
		/**
		 * Widget Object Label
		 */
		Handlebars.registerHelper('widget_label', function(widgetId, widgetLabel, widgetKey, opts) {
			var label = '<strong>' + widgetLabel + '</strong>' + ((defined(widgetKey)) ? '#' + widgetKey: '');
			return new Handlebars.SafeString(
				'<div class="grid-stack-item-label">' +
				'<button type="button" class="btn btn-default btn-sm btn-gridstack-show-details" widget-id="' + widgetId + '" data-toggle="collapse" data-target="#' + widgetId + '-details">' + label + '</button>' +
				'</div>');
		});
		
		/**
		 * Commons Widget Variable (Fetch Variable)
		 */
		Handlebars.registerHelper('widget_var_fetch', function(key, active, opts) {
			var id      = 'var-' + key;
			var display = (active === 'true') ? 'block' : 'none';
			var state   = (active === 'true') ? '' : ' inactive';
			return new Handlebars.SafeString(
				'<div class="form-group var-type" var-type="fetch" widget-id="' + id + '" style="display:' + display + ';">' + 
				'<label for="variable_reference">Commons Variable:</label>' + 
				'<div class="input-group">' +
				'<div class="input-group-addon">LENSE.</div>' +
				'<input type="text" class="form-control var-fetch" placeholder="attrPath" widget-id="' + id + '">' +
				'<x-var type="object" key="var#' + key + '"' + state + '><x-var type="str" key="fetch" prefix="LENSE." value="input.var-fetch[widget-id=\'' + id + '\']"' + state + '></x-var>' + 
				'</div></div>'
			);
		});
		
		/**
		 * Reference Widget Variable
		 */
		Handlebars.registerHelper('widget_var_ref', function(key, active, opts) {
			var id      = 'var-' + key;
			var display = (active === 'true') ? 'block' : 'none';
			var state   = (active === 'true') ? '' : ' inactive';
			return new Handlebars.SafeString(
				'<div class="form-group var-type" var-type="ref" widget-id="' + id + '" style="display:' + display + ';">' + 
				'<label for="variable_reference">Reference:</label>' + 
				'<div class="input-group">' +
				'<div class="input-group-addon">#</div>' +
				'<input type="text" class="form-control var-ref"placeholder="varKey" widget-id="' + id + '">' +
				'<x-var type="str" key="var#'+ key + '" prefix="#" value="input.var-ref[widget-id=\'' + id + '\']"' + state + '>' +
				'</div></div>'
			);
		});
		
		/**
		 * Static Widget Variable
		 */
		Handlebars.registerHelper('widget_var_static', function(key, active, opts) {
			var id      = 'var-' + key;
			var display = (active === 'true') ? 'block' : 'none';
			var state   = (active === 'true') ? '' : ' inactive';
			return new Handlebars.SafeString(
				'<div class="form-group var-type" var-type="static" widget-id="' + id + '" style="display:' + display + ';">' + 
				'<label for="variable_static">Static:</label>' + 
				'<input type="text" class="form-control var-static" placeholder="Static value..." widget-id="' + id + '">' + 
				'<x-var type="str" key="var#' + key + '" value="input.var-static[widget-id=\'' + id + '\']"' + state + '>' + 
				'</div>'
			);
		});
		
		/**
		 * Widget Variable Type
		 */
		Handlebars.registerHelper('widget_var_type', function(type, key, selected, opts) {
			var id = type + '-' + key;
			var selected = (defined(selected)) ? selected: 'static';
			
			// Generate options
			function select_opt(val, label) {
				return (selected == val) ? '<option value="' + val + '" selected="seleceted">' + label + '</option>': '<option value="' + val + '">' + label + '</option>';
			}
			
			// Generate the select block
			return new Handlebars.SafeString(
				'<div class="form-group">' + 
				'<label for="variable_type">Type:</label>' +
				'<select id="variable_type" widget-id="' + id + '" class="form-control">' + 
				select_opt('static', 'Static') + 
				select_opt('ref', 'Reference') +
				select_opt('fetch', 'Commons Variable') + 
				select_opt('call', 'Commons Method') +
				'</select></div>'
			);
		});
		
		/**
		 * Keyed Widget Value
		 */
		Handlebars.registerHelper('widget_key', function(type, key, opts) {
			var id = type + '-' + key;
			return new Handlebars.SafeString(
				'<div class="form-group">' + 
				'<label for="variable_key">Key:</label>' +
				'<input type="text" class="form-control widget-key-value" widget-type="' + type + '" widget-id="' + id + '" value="' + key + '"></div>'
			);
		});
		
		/**
		 * Keyed Widget Header
		 */
		Handlebars.registerHelper('widget_header', function(type, key, opts) {
			var id = (defined(key)) ? type + '-' + key: type;
			return new Handlebars.SafeString('<h4 widget-id="' + id + '"></h4>');
		});
		
		/**
		 * If Equals Conditional
		 */
		Handlebars.registerHelper('ifeq', function(a, b, opts) {
		    if (a == b) {
		    	return opts.fn(this);
		    } else {
		    	return opts.inverse(this);
		    }
		});

		/**
		 * Boolean Form Options
		 */
		Handlebars.registerHelper('boolean_options', function(value, opts) {
			return new Handlebars.SafeString(
				'<option value="true"' + ((value === true) ? ' selected="selected"' : '') + '>Yes</option>' +
				'<option value="false"' + (((value === false) || (!defined(value))) ? ' selected="selected"' : '') + '>No</option>'
			);
		});

		/**
		 * String Form Options
		 */
		Handlebars.registerHelper('string_options', function(value, mapping, opts) {
			options_str = '';
			for (i = 0; i < mapping.length; i++) { 
				if (value == mapping[i]) {
					options_str = options_str.concat('<option selected="selected">' + value + '</option>');
				} else {
					options_str = options_str.concat('<option>' + value + '</option>');
				}
			}
			return new Handlebars.SafeString(options_str);
		})

		/**
		 * Object Title Link
		 */
		Handlebars.registerHelper('title_link', function(uuid, title, opts) {
			return new Handlebars.SafeString('<a href="' +
				window.location.pathname + 
				'?view=' + url.param_get('view') +
				'&uuid=' + uuid + '">' + title + '</a>');
		});

		/**
		 * Stringify JSON
		 */
		Handlebars.registerHelper('json', function(context) {
		    return JSON.stringify(context);
		});

		/**
		 * Boolean To String
		 */
		Handlebars.registerHelper('boolToString', function(bool) {
			return (bool === true) ? new Handlebars.SafeString('Y'): new Handlebars.SafeString('N');
		});

		/**
		 * Object Inspection Link
		 */
		Handlebars.registerHelper('inspect_link', function(uuid) {
			return new Handlebars.SafeString('<button type="button" class="btn btn-default btn-xs glyphicon glyphicon-cog center-block" data-toggle="modal" data-target="#object-inspection" inspect="' + uuid + '"></button>');
		});

		/**
		 * Thumbnail Field
		 */
		Handlebars.registerHelper('thumbnail_field', function(key, value) {
			return new Handlebars.SafeString(
				'<div class="input-group thumbnail-field">' +
				'<span class="input-group-addon thumbnail-field-label" id="basic-addon3">' + key + ':</span>' + 
				'<input type="text" class="thumbnail-field-value form-control" id="basic-url" aria-describedby="basic-addon3" value="' + value + '" readonly>' +
				'</div>'
			);
		});

		/**
		 * Join Array
		 */
		Handlebars.registerHelper('join', function(items) {
			return items.join(',');
		});

		/**
		 * Form Field Generator
		 */
		Handlebars.registerHelper('form_field', function(attrs) {
			var type     = getattr(attrs, 'type');
			var required = (getattr(attrs, 'required', false) ? ' required': '');
			var name     = getattr(attrs, 'name');
			var label    = getattr(attrs, 'label', name);
			var defval   = getattr(attrs, 'defval', '');
			switch(type) {
			
				// Text Input Field
				case 'text':
					return new Handlebars.SafeString(
						'<div class="input-group form-field">' +
						'<span class="input-group-addon form-field-label" id="basic-addon3">' + label + ':</span>' +
						'<input type="text" class="form-control form-field-value" id="basic-addon3" aria-describedby="basic-addon3" name="' + name + '" value=""' + required + ' defval="' + defval + '">' +
						'</div>'
					);
					break;
					
				// Multiline Text Area Field
				case 'textarea':
					return new Handlebars.SafeString(
						'<div class="input-group form-field">' +
						'<span class="input-group-addon form-field-label" id="basic-addon3">' + label + ':</span>' + 
						'<textarea class="form-control form-field-textarea" name="' + name + '" defval="' + defval + '"></textarea>' +
						'</div>'
					);
					break;
					
				// Select Group
				case 'select':
					var options  = getattr(attrs, 'options');
					var selected = getattr(attrs, 'selected', false);
					var defsel   = (selected) ? selected: defval;
					var defopt   = (selected) ? '': '<option selected="selected" value=""></option>';
					function render_options() {
						var options_str = '';
						$.each(options, function(k,v) {
							if ($.isArray(options)) {
								var selected_str = ((selected) && (v == selected)) ? ' selected="selected"': '';
								options_str += '<option value="' + v + '"' + selected_str + '>' + v + '</option>';
							} else {
								var selected_str = ((selected) && (k == selected)) ? ' selected="selected"': '';
								options_str += '<option value="' + v + '"' + selected_str + '>' + k + '</option>';
							}
						})
						return options_str;
					}
					return new Handlebars.SafeString(
						'<div class="input-group form-field">' +
						'<span class="input-group-addon form-field-label" id="basic-addon3">' + label + ':</span>' +
						'<select class="form-control form-field-value form-field-dropdown" aria-describedby="basic-addon3" name="' + name + '" defval="' + defsel + '">' +
						defopt + render_options() +
						'</select></div>'
					);
					break;
					
				// Unsupported
				default:
					throw new Exception('Invalid form field type: ' + type);
			}
		});
	}
	
	/**
	 * Set Template Internals
	 */
	this._set_data = function(data, display, title) {
		var _data_             = {};
		_data_['_DATA_']       = data;
		_data_['_DISPLAY_']    = extract(data, display);
		_data_['_TITLE_']      = getattr(data, title, title);
		_data_['_PATH_']       = window.location.pathname;
		_data_['_METHODS_']    = ["GET", "POST", "PUT", "DELETE"];
		_data_['_VIEW_']       = url.param_get('view');
		_data_['_UUID_']       = url.param_get('uuid');
		_data_['_widgetUUID_'] = lense.uuid4();
		return _data_;
	}
	
	/**
	 * Compile Template
	 */
	this.compile = function(id, data) {
		var compiled = Handlebars.compile($('#' + id).html());
		return compiled(data);
	}
	
	/**
	 * Render Template (Inner)
	 */
	this._render = function(parent, id, data, flush, display, title) {
		
		// Compile the template
		var compiled = Handlebars.compile($('#' + id).html());
		
		// If flushing the container
		if (flush === true) { 
			$(parent).empty(); 
		}
		
		// List of elements
		if ($.isArray(data)) {
			$.each(data, function(i,item) {
				$(parent).append(compiled(self._set_data(item, display, title)));
			});
			
		// Single element
		} else {
			$(parent).append(compiled(self._set_data(data, display, title)));
		}
	}
	/**
	 * Table Headers
	 */
	this._headers = function(parent, columns, title) {
		
		// Compile the template
		var compiled = Handlebars.compile($('#object_row_headers').html());
		
		// Flush the header container
		$(parent).empty();
		
		// Render the headers
		$(parent).append(compiled(self._set_data(columns, {}, title)));
	}
	
	/**
	 * Render Template
	 */
	this.render = function(parent, id, data, options) {
		var callback = getattr(options, 'callback', false);
		var flush    = getattr(options, 'flush', true);
		var display  = getattr(options, 'display', {});
		var title    = getattr(options, 'title', 'name');
		var headers  = getattr(options, 'headers', null);
		
		// Table headers
		if (defined(headers)) {
			self._headers(headers, display, title);
		}
		
		// Array of containers / templates
		if ((parent instanceof Array) && (id instanceof Array)) {
			if (!(parent.length === id.length)) {
				throw new Exception('Parent and template arrays must be the same size!');
			}
			
			// Render each parent / template
			$.each(parent, function(i,p) {
				self._render(p, id[i], data, flush, display, title);
			});
			
		// Single container / template
		} else {
			self._render(parent, id, data, flush, display, title);
		}
		
		// Is a callback specified
		if (callback !== false) { 
			callback(); 
		}
	}
});