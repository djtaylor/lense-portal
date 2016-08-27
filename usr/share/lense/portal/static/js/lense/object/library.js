lense.import('object.library', function() {
	var self  = this;

	// Post processor objects
	this.post = {};

	/**
	 * Post processing
	 */
	this.postProcess = function() {

		// Post processing renderer
		function inner(target, attrs) {
			if (defined(attrs.parent) && $(attrs.parent).is(':empty')) {
				inner(attrs.parent, self.post[attrs.parent]);
			}

			// Only render if empty
			if ($(target).is(':empty')) {
				$(target).html(attrs.html);
			}
		}

		// Loop through post process blocks
		$.each(self.post, function(target,attrs) {
			inner(target, attrs);
		});
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
			lense.common.template.render('#object-controls-create', 'object_create_button', {
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
		 * Add object parameter button
		 *
		 * @param {Object} object The object data
		 */
		Handlebars.registerHelper('object_param_add', function(object, opts) {
			return new Handlebars.SafeString(
				'<div style="overflow:auto;">' +
				'<div class="btn-group pull-right" role="group" object-id="' + object.id + '">' +
				'<button type="button" class="btn btn-default" object-var-add="params" object-id="' + object.id + '" update-source disabled edit>' +
				'<span class="glyphicon glyphicon-plus"></span>' +
				'</button>' +
				'</div></div>'
			);
		});

		/**
		 * Add object variable argument / keyword argument button
		 *
		 * @param {String} object The object data
		 * @param {Array} types Available types to toggle between
		 * @param {String} group The group ID
		 * @param {String} type The object type this should be shown for
		 */
		Handlebars.registerHelper('object_var_add', function(object, types, group, type, opts) {
			var prefix  = getattr(types, 'prefix', '');
			var key     = (hasattr(opts.hash, 'key')) ? ' object-key="' + getattr(opts.hash, 'key') + '"':'';

			// Generate the button HTML
			return new Handlebars.SafeString(
				'<div class="btn-group pull-right" role="group" object-id="' + object.id + '" object-toggle-id="' + prefix + type + '" object-toggle-controls object-toggle-group="' + group + '" style="display:none;">' +
				'<button type="button" class="btn btn-default" object-var-add="' + type + '" object-id="' + object.id + '"' + key + ' update-source disabled edit>' +
				'<span class="glyphicon glyphicon-plus"></span>' +
				'</button>' +
				'</div>'
			);
		});

		/**
		 * Variable argument
		 *
		 * @param {String} id The object ID
		 * @param {String} value The arg value
		 */
		Handlebars.registerHelper('object_var_arg', function(id, value, opts) {
			var value = (defined(value)) ? value:'';

			// Arg / value UUID
			var arg_uuid   = lense.uuid4();
			var value_uuid = lense.uuid4();

			// Generate the keyword argument object
			return new Handlebars.SafeString(
				'<div class="row object-attr-row" object-id="' + id + '" uuid="' + arg_uuid + '">' +
				'<div class="col-xs-11 col-object-center col-object">' +
				'<input type="text" class="form-control object-input" placeholder="value" value="' + value + '" uuid="' + value_uuid + '" update-source disabled edit>' +
				'</div>' +
				'<div class="col-xs-1 col-object-attr-right col-object">' +
				'<button type="button" class="btn btn-danger btn-remove-object-attr" object-id="' + id + '" uuid="' + arg_uuid + '" update-source disabled edit>' +
				'<span class="glyphicon glyphicon-remove"></span>' +
				'</button>' +
				'</div>' +
				'<x-var type="str" value="input[uuid=\'' + value_uuid + '\']"></x-var>' +
				'</div>'
			);
		});

		/**
		 * Variable arguments container
		 */
		Handlebars.registerHelper('object_var_args', function(object, opts) {
			var init_args = [];

			// Generate initial args
			if (defined(object.data.args) && istype(object.data.args, 'array')) {
				$.each(object.data.args, function(i, value) {
					init_args.push(Handlebars.helpers.object_var_arg(object.id, value));
				});
			}

			// Return args container
			return new Handlebars.SafeString(
				'<x-var object-id="' + object.id + '" type="array" key="args" inactive>' +
				init_args.join('') +
				'</x-var>'
			);
		});

		/**
		 * Variable keyword arguments container
		 */
		Handlebars.registerHelper('object_var_kwargs', function(object, opts) {
			var init_kwargs = [];
			var dataKey     = getattr(opts.hash, 'dataKey', 'kwargs');

			// Generate initial kwargs
			if (defined(object.data[dataKey]) && istype(object.data[dataKey], 'object')) {
				$.each(object.data[dataKey], function(key, value) {
					init_kwargs.push(Handlebars.helpers.object_var_kwarg(object.id, key, value));
				});
			}

			// Return kwargs container
			return new Handlebars.SafeString(
				'<x-var object-id="' + object.id + '" type="object" key="' + dataKey + '" inactive>' +
				init_kwargs.join('') +
				'</x-var>'
			);
		});

		/**
		 * Variable keyword argument
		 *
		 * @param {String} id The object ID
		 * @param {String} key The kwarg key
		 * @param {String} value The kwarg value
		 */
		Handlebars.registerHelper('object_var_kwarg', function(id, key, value, opts) {
			return new Handlebars.SafeString(lense.template.html.kwargField(id, ((defined(key)) ? key:''), ((defined(value)) ? value:'')));
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
			var state  = ((getattr(opts.hash, 'active', false) === true) ? '':' inactive');

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
			var xvar        = '<x-var type="' + xvarType + '" key="' + varType + '" value="input[uuid=\'' + uuid + '\']"' + prefix_attr + state + '></x-var>';

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
			return new Handlebars.SafeString('<div data-type="' + type + '" data-parent="" data-element="" style="display:none;" selector="' + getattr(opts.hash, 'selector', type) + '">' + content + '</div>');
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
					return ' aria-label="' + getattr(opts.hash, 'desc') + '"'
				}
				return '';
			}());

			// Data elements / toggle buttons
			var elements   = [];
			var buttons    = {};

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

			// Process data elements
			$(inner).find('[data-element]').each(function() {
				var elem      = $(this);
				var type      = getattr(elem, 'data-type');

				// Element UUID / selected flag
				var elem_uuid = lense.uuid4();
				var selected  = (function() {
					var selector = getattr(elem, 'selector');

					// Select by object key / type
					if (selector.includes('#')) {
						var attrKey  = selector.split('#')[0];
						var attrType = selector.split('#')[1];

						// Check for key / data type
						return ((hasattr(object.data, attrKey) && istype(object.data[attrKey], attrType)) ? true:false);

					// Select by object key
					} else {
						return ((hasattr(object.data, selector)) ? true:false);
					}
				}());

				// Set button UUID
				buttons[type].attr('data-target', elem_uuid);

				// Set group attributes
				elem.attr({
					'data-parent': group_uuid,
					'data-element': elem_uuid
				});

				// Element is selected
				if (selected) {

					// Show the element
					elem.css('display', 'block');

					// Set the parent button attributes
					buttons[type].addClass('active');
				}

				// Store the group element
				elements.push(elem[0].outerHTML);
			});

			// Store elements for post processing
			self.post[target] = {
				html: elements.join(''),
				parent: parent
			};

			// Return group toggler
			return new Handlebars.SafeString(
				'<div class="btn-group btn-group-inner" role="group"' + label + '>' +
				(Object.keys(buttons).map(function(key){return buttons[key][0].outerHTML}).join('')) +
				'</div>'
			);
		});

		/**
		 * Object parameter
		 *
		 * @param {Object} object The object data
		 * @param {Object} param The parameter data
		 */
		Handlebars.registerHelper('object_param', function(object, key, attrs, opts) {

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
				'<div class="row object-attr-row" object-id="' + object.id + '" uuid="' + param_uuid + '">' +
				'<div class="col-xs-5 col-object-center col-object">' +
				'<input type="text" class="form-control object-input" placeholder="value" value="' + key + '" uuid="' + key_uuid + '" update-source disabled edit>' +
				'</div>' +
				'<div class="col-xs-1 col-object-center col-object">' +
				'<input class="col-object-checkbox" type="checkbox"' + req_checked + ' uuid="' + req_uuid + '" update-source disabled edit>' +
				'<x-var type="bool" value="input[uuid=\'' + req_uuid + '\']"></x-var>' +
				'</div>' +
				'<div class="col-xs-5 col-object-center col-object" style="padding-left:15px;">' +
				'<input type="text" class="form-control object-input" placeholder="none" value="' + ((defined(attrs[1])) ? attrs[1]:'') + '" uuid="' + def_uuid + '" update-source disabled edit>' +
				'<x-var type="str" value="input[uuid=\'' + def_uuid + '\']" default="null"></x-var>' +
				'</div>' +
				'<div class="col-xs-1 col-object-attr-right col-object">' +
				'<button type="button" class="btn btn-danger btn-remove-object-attr" object-id="' + object.id + '" uuid="' + param_uuid + '" disabled edit>' +
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
					init_params.push(Handlebars.helpers.object_param(object, key, attrs));
				});

				// Return kwargs container
				return new Handlebars.SafeString('<div class="form-group">' + init_params.join('') + '</div>');
			}
		});

		/**
		 * Object Property
		 *
		 * @param {object} key The property key
		 * @param {Object} data The property data
		 * @param {Object} properties Properties options
		 */
		Handlebars.registerHelper('object_property', function(key, data, template, opts) {
			template.each(function(k, attrs) {
				if (k === key)
			});

			var type  = getattr(properties, 'type', 'str');
			var edit  = (function() {
				var canEdit = getattr(properties, 'edit', false);
				return ((canEdit) ? ' edit':'');
			}());
			var label = getattr(properties, 'label', key);
			var uuid  = lense.uuid4();
			var local = data[key];

			// Generate the object property HTML
			return new Handlebars.SafeString(
				'<div class="input-group property-field">' +
				'<span class="input-group-addon property-field-label">' + label + '</span>' +
				(function() {
					switch(type) {
						case 'str':
							return new Handlebars.SafeString(
								'<input type="text" class="form-control property-field-value" value="' + local + '" uuid="' + uuid + '"disabled update-source' + edit + '>' +
								'<x-var type="str" key="' + key + '" value="input[uuid=\'' + uuid + '\']"></x-var>'
							);
						case 'bool':
							var options = getattr(properties, 'options', [true, false]);
							return new Handlebars.SafeString(
								'<select class="form-control property-field-value property-field-dropdown" uuid="' + uuid + '" disabled update-source' + edit + '>' +
								(function() {
									var fields = [];
									$.each([true, false], function(i,state) {
										opt_value = ((istype(state, 'array')) ? state[0]:state);
										opt_label = ((istype(state, 'array')) ? state[1]:((opt_value === true) ? 'Yes':'No'));
										opt_state = ((local === opt_value) ? ' selected="selected"':'');
										fields.push('<option value="' + opt_value + '"' + opt_state + '>' + opt_label + '</option>');
									});
									return fields.join('');
								}()) +
								'</select>' +
								'<x-var type="bool" key="' + key + '" value="select[uuid=\'' + uuid +  '\']"></x-var>'
							);
						case 'select':
							var options = getattr(properties, 'options');
							return new Handlebars.SafeString(
								'<select class="form-control property-field-value property-field-dropdown" uuid="' + uuid + '" disabled update-source' + edit + '>' +
								(function() {
									var fields = [];
									$.each(options, function(i,value) {
										opt_value = ((istype(value, 'array')) ? value[0]:value);
										opt_label = ((istype(value, 'array')) ? value[1]:opt_value);
										opt_state = ((local == opt_value) ? ' selected="selected"':'');
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
		 * @param {Object} properties Visible row properties
		 * @param {Object} opts Any additional options
		 */
		Handlebars.registerHelper('object_thumbnail', function(object, properties, opts, handlebarOpts) {
			return new Handlebars.SafeString(lense.template.html.objectThumbnail(object, {
				title_name: object[getattr(opts, 'title')],
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
