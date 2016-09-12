lense.import('object.library', function() {
	var self  = this;

	// Render processor storage
	this.store = {};

	/**
	 * Post object creation rendering
	 */
	this.render = function() {
		function renderWorker(target, attrs) {
			if (defined(attrs.parent) && $(attrs.parent).is(':empty')) {
				renderWorker(attrs.parent, self.store[attrs.parent]);
			}

			// Only render if empty
			if ($(target).is(':empty')) {
				$(target).html(attrs.html);
			}
		}

		// Loop through post process blocks
		$.each(self.store, function(target,attrs) {
			renderWorker(target, attrs);
		});

		// Bootstrap toggle
		$('[data-toggle="toggle"]').bootstrapToggle();
	}

	/**
	 * Base Object
	 */
	function BaseObject(opts) {
		var inner     = this;

		// Object attributes
		this.type     = getattr(opts, 'type');
		this.template = getattr(opts, 'template');
		this.label    = getattr(opts, 'label', this.type);
		this.keyed    = getattr(opts, 'keyed', false);
		this.map      = getattr(opts, 'map', false);

		// Object setup method
		this.setup = function() {

			// New object button
			lense.template.render('#object-controls-create', 'object_create_button', {
				type: inner.type,
				label: inner.label,
				keyed: inner.keyed,
			},
			{
				flush: false
			});
		}

		/**
		 * Create a new object instance.
		 *
		 * @param {String} container The parent container
		 * @param {String} key An optional object key
		 * @param {Object} data The object data
		 */
		this.create = function(grid, key, data) {
			try {
				var id = (defined(key)) ? inner.type + '-' + key: inner.type;

				// Create the parent object widget
				var widget = lense.template.compile('object_widget', {
					id: id,
					key: key,
					type: inner.type,
					label: inner.label,
					map: inner.map
				}).html();

				// Create the widget
				grid.data('gridstack').addWidget(widget);

				// Create object details
				$('.object-attrs-body[object-id="' + id + '"]').append(lense.template.compile(inner.template, {
					object: {
						id: id,
						key: key,
						type: inner.type,
						label: inner.label,
						map: inner.map,
						data: data
					},
					meta: {
						varTypes: [
							{
								type: 'call',
								label: 'Lense Method',
								selector: 'call'
							},
							{
								type: 'fetch',
								label: 'Lense Variable',
								selector: 'fetch'
							},
							{
								type: 'static',
								label: 'Static Value',
								selector: 'static'
							},
							{
								type: 'ref',
								label: 'Referenced Value',
								selector: 'ref'
							}
						],
						argTypes: [
							{
								type: 'ref',
								label: 'Reference',
								selector: 'args::string'
							},
							{
								type: 'list',
								label: 'List',
								selector: 'args::array'
							}
						],
						kwargTypes: [
							{
								type: 'ref',
								label: 'Reference',
								selector: 'kwargs::string'
							},
							{
								type: 'dict',
								label: 'Dictionary',
								selector: 'kwargs::object'
							}
						],
						rspTypes: [
							{
								type: 'ref',
								label: 'Reference',
								selector: 'data::string'
							},
							{
								type: 'dict',
								label: 'Dictionary',
								selector: 'data::object'
							}
						]
					}
				}).html());
			} catch(e) {
				lense.log.warn(e);
			}
		}
	}

	/**
	 * Map object type to interface.
	 *
	 * @param {String} type The object type.
	 */
	this.mapType = function(type) {
		switch(type) {
			case "var":
			  return self.HandlerVariable;
			case "__PARAMS__":
			  return self.HandlerParameters;
		  case "response":
			  return self.HandlerResponse;
			case "do":
			  return self.HandlerAction;
			default:
				lense.log.warn('Invalid grid object type: ' + type);
				break;
		}
	}

	/**
	 * Handler Variable
	 */
	this.HandlerVariable = new BaseObject({
		type: 'var',
		label: 'variable',
		template: 'object_type_variable',
		keyed: true
	});

	/**
	 * Handler Parameters
	 */
	this.HandlerParameters = new BaseObject({
		type: 'params',
		label: 'parameters',
		map: '__PARAMS__',
		template: 'object_type_parameters'
	});

	/**
	 * Handler Response
	 */
	this.HandlerResponse = new BaseObject({
		type: 'response',
		template: 'object_type_response'
	});

	/**
	 * Handler Action
	 */
	this.HandlerAction = new BaseObject({
		type: 'do',
		label: 'action',
		template: 'object_type_action',
		keyed: true
	});

	/**
	 * @constructor
	 */
	lense.register.constructor('object.library', function() {

		/**
		 * Button for adding a new argument variable
		 *
		 * @param {String} type The argument type
		 * @param {Object} object The data object
		 */
		Handlebars.registerHelper('object_arg_add', function(type, object, opts) {
			var dataKey = getattr(opts.hash, 'dataKey', ((type === 'kwarg') ? 'kwargs':'args'));

			// Generate the argument button
			return new Handlebars.SafeString(
				'<div class="btn-group pull-right" role="group" object-id="' + object.id + '">' +
				'<button type="button" class="btn btn-default" object-arg-add="' + type + '" object-id="' + object.id + '" data-key="' + dataKey + '" update-source disabled edit>' +
				'<span class="glyphicon glyphicon-plus"></span>' +
				'</button>' +
				'</div>'
			);
		});

		/**
		 * Object argument
		 *
		 * @param {String} type The argument type: arg, kwarg
		 * @param {String} id The object ID
		 * @param {Object} map Object key/value mapping
		 */
		Handlebars.registerHelper('object_arg', function(type, id, map, opts) {

			// Generated HTML
			var html;

			// Process based on type
			switch(type) {
				case "arg":
					html = lense.template.html.argField(id, getattr(map, 'value', ''));
					break;
				case "kwarg":
					html = lense.template.html.kwargField(id, getattr(map, 'key', ''), getattr(map, 'value', ''));
					break;
				default:
					lense.raise('Invalid argument type: ' + type);
			}

			// Return the argument element
			return new Handlebars.SafeString(html);
		});

		/**
		 * Variable arguments container
		 */
		Handlebars.registerHelper('object_args', function(object, opts) {
			var args = [];

			// Generate initial args
			if (defined(object.data.args) && istype(object.data.args, 'array')) {
				$.each(object.data.args, function(i, value) {
					args.push(Handlebars.helpers.object_arg('arg', object.id, { 'value': value }));
				});
			}

			// Return args container
			return new Handlebars.SafeString(
				'<x-var object-id="' + object.id + '" type="array" key="args">' +
				args.join('') +
				'</x-var>'
			);
		});

		/**
		 * Variable keyword arguments container
		 */
		Handlebars.registerHelper('object_kwargs', function(object, opts) {
			var kwargs  = [];
			var dataKey = getattr(opts.hash, 'dataKey', 'kwargs');

			// Generate initial kwargs
			if (defined(object.data[dataKey]) && istype(object.data[dataKey], 'object')) {
				$.each(object.data[dataKey], function(key, value) {
					kwargs.push(Handlebars.helpers.object_arg('kwarg', object.id, { 'key': key, 'value': value }));
				});
			}

			// Return kwargs container
			return new Handlebars.SafeString(
				'<x-var object-id="' + object.id + '" type="object" key="' + dataKey + '">' +
				kwargs.join('') +
				'</x-var>'
			);
		});

		/**
		 * Object variable input
		 *
		 * @param {String} xvarType The variable type for the x-var entry
		 * @param {String} varType The variable type for the object data
		 * @param {Object} object The data object
		 * @param {String} opts.prefix The data prefix
		 */
		Handlebars.registerHelper('object_var_input', function(xvarType, varType, object, opts) {
			var uuid   = lense.uuid4();
			var prefix = getattr(opts.hash, 'prefix', false);
			var style  = ((hasattr(opts.hash, 'style')) ? ' style="' + getattr(opts.hash, 'style') + '"':'');

			// Extract the value if present
			var value = (function() {
				if (istype(object.data[varType], 'str')) {
					if (defined(prefix)) {
						return (hasattr(object.data, varType)) ? ' value="' + object.data[varType].replace(prefix, '') + '"':'';
					} else {
						return (hasattr(object.data, varType)) ? ' value="' + object.data[varType] + '"':'';
					}
				} else {
					return '';
				}
			}());

			// Generate the input field and variable object
			var prefix_attr = (defined(prefix)) ? ' prefix="' + prefix + '"':'';
			var input       = '<input type="text" class="form-control" object-var-type="' + varType + '" object-id="' + object.id + '" uuid="' + uuid + '"' + value + ' update-source disabled edit>';
			var xvar        = '<x-var type="' + xvarType + '" key="' + varType + '" value="input[uuid=\'' + uuid + '\']"' + prefix_attr + '></x-var>';

			// Input group
			if (defined(prefix)) {
				return new Handlebars.SafeString('<div class="input-group"><div class="input-group-addon">' + prefix + '</div>' + input + xvar + '</div>');
			} else {
				return new Handlebars.SafeString('<div class="form-group"' + style + '>' + input + xvar + '</div>');
			}
		});

		/**
		 * Data element
		 *
		 * @param {String} type The data element type
		 */
		Handlebars.registerHelper('data_element', function(type, opts) {
			var content = (function() {
				if (hasattr(opts.hash, 'content')) {
					return $('<div class="data-element">' + opts.hash.content.string + '</div>')[0].outerHTML
				}
				return $('<div class="data-element">' + opts.fn(this) + '</div>')[0].outerHTML;
			}());

			// Return the data element
			return new Handlebars.SafeString('<div data-type="' + type + '" data-parent="" data-element="" style="display:none;" data-selector="' + getattr(opts.hash, 'selector', type) + '">' + content + '</div>');
		});

		/**
		 * Data group
		 *
		 * @param {Object} object The data object
		 * @param {String} target The target container for child groups
		 * @param {Object} types A type map for the data group
		 */
		Handlebars.registerHelper('data_group', function(object, target, types, opts) {
			var inner      = $('<div class="data-group">' + opts.fn(this) + '</div>');
			var append     = (hasattr(opts.hash, 'append') ? opts.hash.append.string:false)
			var target     = (function() {
				return '#' + (defined(object.key) ? target + '-' + object.key:target);
			}());
			var parent     = (function() {
				var parentStr = getattr(opts.hash, 'parent', false);
				if (parentStr) {
					return '#' + (defined(object.key) ? parentStr + '-' + object.key:parentStr);
				}
				return false;
			}());
			var label      = (function() {
				if (hasattr(opts.hash, 'desc')) {
					return ' aria-label="' + getattr(opts.hash, 'desc') + '"';
				}
				return '';
			}());

			// UUIDs by data type
			var type_uuids = {};

			// Data elements / toggle buttons
			var elements   = [];
			var buttons    = {};

			// Group controls container
			var controls   = {};

			// Group UUID
			var group_uuid = lense.uuid4();

			// Generate toggle buttons
			$.each(types, function(i,attrs) {
				buttons[attrs.type] = $(lense.template.html.button(attrs.label, {
					attrs: {
						'data-group': group_uuid,
						'object-id': object.id,
						'update-source': true,
						'disabled': true,
						'edit': true
					}
				}));
			});

			// Data storage
			var data_store = {
				'inner': [],
				'append': ''
			};

			// Process data elements
			function process_element(elem, loc) {
				var loc       = (defined(loc) ? loc:'inner');
				var type      = getattr(elem, 'data-type');

				// Element UUID / selected flag
				var elem_uuid = (function() {
					if (hasattr(type_uuids, type)) {
						return type_uuids[type];
					}
					type_uuids[type] = lense.uuid4();
					return type_uuids[type];
				}());

				// Is the element selected
				var selected  = (function() {
					var selector = getattr(elem, 'data-selector');

					// Select by object key / type
					if (selector.includes('#')) {
						var attr = selector.split('#');

						// Check for key / data type
						return ((hasattr(object.data, attr[0]) && istype(object.data[attr[0]], attr[1])) ? true:false);

					// Select by object key
					} else {
						return ((hasattr(object.data, selector)) ? true:false);
					}
				}());

				// Set button UUID
				if (hasattr(buttons, type)) {
					buttons[type].attr('data-target', elem_uuid);
				}

				// Set group attributes
				elem.attr({
					'data-parent': group_uuid,
					'data-element': elem_uuid
				});

				// Variable state
				var state = (selected ? '':' inactive');

				// Element is selected
				if (selected) {
					elem.css('display', 'block');
					buttons[type].addClass('active');
				}

				// Process the location
				switch(loc) {
					case "inner":
						data_store[loc].push('<x-var type="meta" data-parent="' + group_uuid + '" data-element="' + elem_uuid + '"' + state + '>' + elem[0].outerHTML + '</x-var>');
						break;
					case "append":
						data_store[loc] = '<div class="btn-group pull-right" role="group" object-id="' + object.id + '">' + elem[0].outerHTML + '</div>';
						break;
					default:
						lense.raise('Invalid element location: ' + loc);
				}
			}

			// Process inner data elements
			$(inner).find('[data-element]').each(function() {
				process_element($(this));
			});

			// Any extra HTML to append inside the button group
			if (defined(append)) { process_element($(append), 'append'); }

			// Store elements for post processing
			self.store[target] = {
				html: data_store.inner.join(''),
				parent: parent
			};

			// Return group toggler
			return new Handlebars.SafeString(
				'<div class="btn-group btn-group-inner" role="group"' + label + '>' +
				(function() {
					var btnsHTML = [];
					$.each(buttons, function(type, btnHTML) {
						btnsHTML.push(btnHTML[0].outerHTML);
					});
					return btnsHTML.join('');
				}()) +
				'</div>' + (defined(data_store.append) ? data_store.append:'')
			);
		});

		/**
		 * Object perissions row
		 */
		Handlebars.registerHelper('object_permissions', function(object) {
			var size = 'mini';
			return new Handlebars.SafeString(
				'<tr>' +
				'<th>' + object.owner + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.user_read, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.user_write, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.user_delete, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.user_exec, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.group_read, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.group_write, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.group_delete, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.group_exec, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.all_read, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.all_write, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.all_delete, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.all_exec, 'size': size }) + '</th>' +
				'<th>' + lense.template.html.boolToggle({ 'uuid': lense.uuid4(), 'selected': object.share, 'size': size }) + '</th>' +
				'</tr>'
			);
		});

		/**
		 * Object parameter
		 *
		 * @param {Object} object The object data
		 * @param {Object} param The parameter data
		 */
		Handlebars.registerHelper('object_param', function(oid, key, attrs, opts) {

			// UUIDs
			var param_uuid  = lense.uuid4();
			var key_uuid    = lense.uuid4();
			var req_uuid    = lense.uuid4();
			var def_uuid    = lense.uuid4();

			// Required checked state
			var req_checked = (attrs[0] === true) ? ' checked':'';

			// Generate parameter HTML
			return new Handlebars.SafeString(
				'<x-var type="array" key="@input[uuid=\'' + key_uuid + '\']">' +
				'<div class="row object-attr-row" object-id="' + oid + '" uuid="' + param_uuid + '">' +
				'<div class="col-xs-5 col-object-left col-object">' +
				'<input type="text" class="form-control object-input" placeholder="value" value="' + key + '" uuid="' + key_uuid + '" update-source disabled edit>' +
				'</div>' +
				'<div class="col-xs-4 col-object-center col-object">' +
				'<input type="text" class="form-control object-input" placeholder="none" value="' + ((defined(attrs[1])) ? attrs[1]:'') + '" uuid="' + def_uuid + '" update-source disabled edit>' +
				'<x-var type="str" value="input[uuid=\'' + def_uuid + '\']" default="null"></x-var>' +
				'</div>' +
				'<div class="col-xs-2 col-object-center col-object">' +
				lense.template.html.boolToggle({
					'uuid': req_uuid,
					'selected': (defined(attrs[0]) ? attrs[0]:false)
				}) +
				'<x-var type="bool" value="input[uuid=\'' + req_uuid + '\']"></x-var>' +
				'</div>' +
				'<div class="col-xs-1 col-object-attr-right col-object">' +
				'<button type="button" class="btn btn-danger btn-remove-object-attr" object-id="' + oid + '" uuid="' + param_uuid + '" disabled edit>' +
				'<span class="glyphicon glyphicon-remove"></span>' +
				'</button>' +
				'</div>' +
				'</div></x-var>'
			);
		});

		/**
		 * Object parameters
		 *
		 * @param {Object} object The data object
		 */
		Handlebars.registerHelper('object_params', function(object, opts) {
			if (hasattr(object, 'data') && istype(object.data, 'object')) {
				var init_params = [];

				// Generate initial parameters
				$.each(object.data, function(key, attrs) {
					init_params.push(Handlebars.helpers.object_param(object.id, key, attrs));
				});

				// Return kwargs container
				return new Handlebars.SafeString('<div class="form-group"><x-var type="object" key="__PARAMS__">' + init_params.join('') + '</x-var></div>');
			}
		});

		/**
		 * Object Property
		 *
		 * @param {object} key The property key
		 * @param {Object} data The property data
		 * @param {Object} template Properties template
		 */
		Handlebars.registerHelper('object_property', function(key, data, template, opts) {
			var type  = getattr(template, 'type', 'str');
			var edit  = (function() {
				var canEdit = getattr(template, 'edit', false);
				return ((canEdit) ? ' edit':'');
			}());
			var label = getattr(template, 'label', key);
			var uuid  = lense.uuid4();

			// Generate the object property HTML
			return new Handlebars.SafeString(
				'<div class="input-group property-field">' +
				'<span class="input-group-addon property-field-label">' + label + '</span>' +
				(function() {
					switch(type) {
						case 'str':
							return new Handlebars.SafeString(
								'<input type="text" class="form-control property-field-value" value="' + data + '" uuid="' + uuid + '"disabled update-source' + edit + '>' +
								'<x-var type="str" key="' + key + '" value="input[uuid=\'' + uuid + '\']"></x-var>'
							);
						case 'bool':
							var options = getattr(template, 'options', [true, false]);
							return new Handlebars.SafeString(
								'<select class="form-control property-field-value property-field-dropdown" uuid="' + uuid + '" disabled update-source' + edit + '>' +
								(function() {
									var fields = [];
									$.each([true, false], function(i,state) {
										opt_value = ((istype(state, 'array')) ? state[0]:state);
										opt_label = ((istype(state, 'array')) ? state[1]:((opt_value === true) ? 'Yes':'No'));
										opt_state = ((data === opt_value) ? ' selected="selected"':'');
										fields.push('<option value="' + opt_value + '"' + opt_state + '>' + opt_label + '</option>');
									});
									return fields.join('');
								}()) +
								'</select>' +
								'<x-var type="bool" key="' + key + '" value="select[uuid=\'' + uuid +  '\']"></x-var>'
							);
						case 'select':
							var options = getattr(template, 'options');
							return new Handlebars.SafeString(
								'<select class="form-control property-field-value property-field-dropdown" uuid="' + uuid + '" disabled update-source' + edit + '>' +
								(function() {
									var fields = [];
									$.each(options, function(i,value) {
										opt_value = ((istype(value, 'array')) ? value[0]:value);
										opt_label = ((istype(value, 'array')) ? value[1]:opt_value);
										opt_state = ((data == opt_value) ? ' selected="selected"':'');
										fields.push('<option value="' + opt_value + '"' + opt_state + '>' + opt_label + '</option>');
									});
									return fields.join('');
								}()) +
								'</select>' +
								'<x-var type="str" key="' + key + '" value="select[uuid=\'' + uuid +  '\']"></x-var>'
							);
						default:
							lense.log.warn('Invalid property type: ' + type);
							return undefined;
					}
				}()) +
				'</div>'
			);
		});

		/**
		 * Object widget helper
		 */
		Handlebars.registerHelper('object_widget', function(id, type, key, map, opts) {
			object_key   = ((defined(key)) ? ' object-key="' + key + '"': '');
			object_map   = ((defined(map)) ? ' object-map="' + map + '"': '');
			widget_attrs = 'object-id="' + id + '" object-type="' + type + '"' + object_key + object_map;
			grid_attrs   = 'data-gs-width="12" data-gs-height="1" data-gs-auto-position="true" data-gs-no-resize="true" ';

			// Return the HTML object
			return new Handlebars.SafeString(
				'<div class="grid-stack-item" ' + grid_attrs + widget_attrs + '>' +
				'<x-var type="object">' +
				opts.fn(this) + '</x-var></div>');
		});

		/**
		 * Object label helper
		 */
 		Handlebars.registerHelper('object_label', function(id, label, key, opts) {
 			var label = '<strong>' + label + '</strong>' + ((defined(key)) ? '#' + key: '');
 			return new Handlebars.SafeString(
 				'<div class="grid-stack-item-label">' +
 				'<button type="button" class="btn btn-default btn-sm object-show-details text-capitalize" object-id="' + id + '" data-toggle="collapse" data-target="#' + id + '-details">' + label + '</button>' +
 				'</div>');
 		});

		/**
		 * Object row
		 *
		 * @param {Object} object The row object data
		 * @param {Object} template The object template
		 */
		Handlebars.registerHelper('object_row', function(object, template, opts) {
			return new Handlebars.SafeString(lense.template.html.objectRow(object, {
				template: template,
				title_link: window.location.pathname + '?view=' + lense.url.getParam('view') + '&uuid=' + object.uuid + '"'
			})).string;
		});

		/**
		 * Object thumbnail
		 *
		 * @param {Object} object The row object data
		 * @param {Object} template Object template
		 */
		Handlebars.registerHelper('object_thumbnail', function(object, template, opts) {
			var title_attr = null;
			template.each(function(k,obj) {
				if (getattr(obj, 'link', false) === true) {
					title_attr = k;
				}
			});
			return new Handlebars.SafeString(lense.template.html.objectThumbnail(object, {
				title_name: getattr(object, title_attr, object.uuid),
				title_link: window.location.pathname + '?view=' + lense.url.getParam('view') + '&uuid=' + object.uuid + '"',
				template: template
			})).string;
		});

		/**
		 * Object row headers
		 *
		 * @param {Object} template Object template
		 */
		Handlebars.registerHelper('object_headers', function(template, opts) {
			return new Handlebars.SafeString(lense.template.html.objectHeaders(template));
		});

		/**
		 * Manage objects
		 */
		Handlebars.registerHelper('manage_objects', function(opts) {
			return new Handlebars.SafeString(
				lense.template.html.button('Delete', {
					type: 'danger',
					modal: 'object-delete'
				}) +
				lense.template.html.buttonLink('Create', {
					params: {
						view: lense.url.getParam('view'),
						create: true
					}
				})
			);
		});

		/**
		 * Sort options
		 *
		 * @param {Object} template The object template
		 */
		Handlebars.registerHelper('sort_objects', function(template, opts) {
			return new Handlebars.SafeString(
				'<span class="input-group-addon thumbnail-field-label thumbnail-field-label-inline">Sort: </span>' +
				'<select class="form-control property-field-value property-field-dropdown property-field-inline" object-sort>' +
				(function() {
					var options = [lense.template.html.selectOption(null, {
						label: 'Please select...'
					})];
					template.each(function(key, attrs) {
						if (attrs.list) {
							options.push(lense.template.html.selectOption(key, { label: getattr(attrs, 'label', key)}));
						}
					});
					return options.join('');
				}()) +
				'</select>'
			);
		});
	});
});
