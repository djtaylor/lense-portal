lense.import('object.library', function() {
	var self = this;

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
		 * Expand object details
		 *
		 * @param {Object} grid The gridstack object
		 * @param {String} id The object ID
		 */
		this.resizeDetails = function(grid, id) {
			var height = $('.object-collapse[object-id="' + id + '"]').actual('height');
			var ysize  = Math.ceil(height / 40);

			// Resize the widget
			grid.data('gridstack').resize('.grid-stack-item[object-id="' + id + '"]', null, (ysize == 1) ? 2: ysize);
		}

		/**
		 * Collapse object details
		 *
		 * @param {Object} grid The gridstack object
		 * @param {String} id The object ID
		 */
		this.collapseDetails = function(grid, id) {
			grid.data('gridstack').resize('.grid-stack-item[object-id="' + id + '"]', null, 1);
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
						varTypes: {
							list: [
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
							]
						},
						argTypes: {
							prefix: 'args-',
							list: [
								{
									type: 'ref',
									prefix: 'args',
									label: 'Reference',
									selector: 'args::string'
								},
								{
									type: 'list',
									prefix: 'args',
									label: 'List',
									selector: 'args::array'
								}
							]
						},
						kwargTypes: {
							prefix: 'kwargs-',
							list: [
								{
									type: 'ref',
									prefix: 'kwargs',
									label: 'Reference',
									selector: 'kwargs::string'
								},
								{
									type: 'dict',
									prefix: 'kwargs',
									label: 'Dictionary',
									selector: 'kwargs::object'
								}
							]
						}
					}
				}).html());

				// Show object details
				$(document).on('shown.bs.collapse', '.object-collapse[object-id="' + id + '"]', function() {
					inner.resizeDetails(grid, id);
				});

				// Hide widget details
				$(document).on('hidden.bs.collapse', '.object-collapse[object-id="' + id + '"]', function() {
					inner.collapseDetails(grid, id);
				});

				// Toggler groups
				$(document).on('click', 'button[object-toggle-target]', function() {
					var target       = getattr($(this), 'object-toggle-target');
					var group        = getattr($(this), 'object-toggle-group');

					// jQuery selectors
					var btn_all      = 'button[object-id="' + id + '"][object-toggle-group="' + group + '"]';
					var btn_selected = 'button[object-id="' + id + '"][object-toggle-group="' + group + '"][object-toggle-target="' + target + '"]';
					var grp_all      = 'div[object-id="' + id + '"][object-toggle-group="' + group + '"]';
					var grp_selected = 'div[object-id="' + id + '"][object-toggle-group="' + group + '"][object-toggle-id="' + target + '"]';

					// Only execute if target ID is hidden
					if ($(grp_selected).css('display') == 'none') {

						// Switch button states
						$(btn_all).attr('class', 'btn btn-default');
						$(btn_selected).attr('class', 'btn btn-default active');

						// Toggle groups
						$(grp_all).css('display', 'none');
						$(grp_selected).css('display', 'block');
					}

					// Resize widget
					inner.resizeDetails(grid, id);
				});

			} catch(e) {
				lense.notify('warning', e);
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
				lense.notify('warning', 'Invalid grid object type: ' + type);
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
		 * Object Variable Input
		 */
		Handlebars.registerHelper('object_var_input', function(xvarType, varType, object, opts) {
			var uuid  = lense.uuid4();
			var input = '<input type="text" class="form-control" object-var-type="' + varType + '" object-id="' + object.id + '" uuid="' + uuid + '">';
			var xvar  = '<x-var type="' + xvarType + '" key="' + varType + '" value="input[uuid=\'' + uuid + '\']"></x-var>';

			// Return the input object
			return new Handlebars.SafeString(input + xvar);
		});

		/**
		 * Object Toggler
		 *
		 * Buttons to toggle between available type groups for an object widget.
		 *
		 * @param {String} id The parent object ID
		 * @param {Array} types Available types to toggle between
		 * @param {Object} data The toggled object data
		 * @param {String} def The default option to select
		 * @param {String} gid The group ID
		 */
		Handlebars.registerHelper('object_toggler', function(id, types, data, def, gid, opts) {
			var buttons = [];
			var usedef  = true;
			var prefix  = getattr(types, 'prefix', '');

			// Check if using the default
			$.each(types.list, function(i, attrs) {
				var selector = getattr(attrs, 'selector');
				if ($.isArray(selector)) {
					if (hasattr(data, selector[0])) {
						usedef = false;
					}
				} else {
					if (hasattr(data, selector)) {
						usedef = false;
					}
				}
			});

			// Button generator
			function makeButton(type, label, selected) {
				var state = (selected === true || (usedef === true && type == prefix + def)) ? ' active':'';
				return '<button type="button" class="btn btn-default' + state + '" object-id="' + id + '" object-toggle-target="' + type + '" object-toggle-group="' + gid + '">' + label + '</button>';
			}

			// Process object types
			$.each(types.list, function(i,attrs) {
				var type     = getattr(attrs, 'type');
				var label    = getattr(attrs, 'label');
				var selector = getattr(attrs, 'selector');

				// Select by value
				if ($.isArray(selector)) {
					buttons.push((hasattr(data, selector[0]) && data[selector[0]] == selector[1]) ? makeButton(prefix + type, label, true):makeButton(prefix + type, label, false));

				// Select by attribute existence/type
				} else {

					// Attribute existence and type
					if (selector.includes('::')) {
						var typeMap = selector.split('::');

						// Generate the button
						buttons.push((hasattr(data, typeMap[0]) && istype(data[typeMap[0]], typeMap[1])) ? makeButton(prefix + type, label, true):makeButton(prefix + type, label, false));

					// Attribute existence only
					} else {
						buttons.push((hasattr(data, selector)) ? makeButton(prefix + type, label, true):makeButton(prefix + type, label, false));
					}
				}
			});
			return new Handlebars.SafeString('<div class="btn-group" role="group" aria-label="DescriptiveText">' + buttons.join('') + '</div>');
		});

		/**
		 * Object Toggler Group
		 *
		 * Group element for an object toggler.
		 *
		 * @param {String} id The parent object ID
		 * @param {Array} types All available toggler types
		 * @param {Object} data The current object data
		 * @param {String} current The current object type
		 * @param {String} gid The toggle group ID
		 */
		Handlebars.registerHelper('object_toggler_group', function(id, types, data, current, gid, opts) {
				var display = 'none';
				var usedef  = true;
				var prefix  = getattr(types, 'prefix', '');

				// Scan available types
				$.each(types.list, function(i,attrs) {
					var type     = getattr(attrs, 'type');
					var label    = getattr(attrs, 'label');
					var selector = getattr(attrs, 'selector');

					// If checking the current type
					if (current == type) {

						// Select by value
						if ($.isArray(selector)) {
							display = (hasattr(data, selector[0]) && data[selector[0]] == selector[1]) ? 'block':'none';

						// Select by attribute existence
						} else {

							// Attribute existence and type
							if (selector.includes('::')) {
								var typeMap = selector.split('::');

								// Set initial display property
								display = (hasattr(data, typeMap[0]) && istype(data[typeMap[0]], typeMap[1]) ? 'block':'none');

							// Attribute existence only
							} else {
								display = (hasattr(data, selector)) ? 'block':'none';
							}
						}
					}
				});
				return new Handlebars.SafeString('<div object-toggle-id="' + prefix + current + '" object-toggle-group="' + gid + '" object-id="' + id + '" style="display:' + display + ';">' + opts.fn(this) + '</div>');
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
	});
});
