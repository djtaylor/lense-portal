lense.import('admin.models', function() {
	var self = this;

	// Object definition
	//this.object = lense.object.define('handler', url.param_get('uuid'));
	this.object = lense.object.define('handler', 'f71a6563-bfbf-469e-bf5e-386a5c573c52');

	this.defineActions = function() {}

	/**
	 * Define Widget HTML
	 */
	//this.object.defineWidget('manifest_object', function() {});

	/**
	 * Register Object Helpers
	 */
	this.registerObjectHelpers = function() {

		/**
		 * Add Keyed Widget
		 */
		lense.common.object.registerHelper('manifest', 'addKeyedWidget', function(id, e) {
			var widget_type  = $('#keyed-widget-type').val();
			var widget_id    = widget_type + '-' + k;
			var widget_label = getattr($(e), 'widget-label', widget_type);

			// Duplicate key
			if ($('div[widget-id="' + widget_id + '"]').length > 0) {
				$('#object-key-error').html('The ' + widget_id + ' object is already defined!');
				$('#object-key-error').css('display', 'block');
				return false;
			}

			// Close the modal
			$('#object-key-error').html('');
			$('#object-key-error').css('display', 'none');
			$('#object-key').modal('toggle');
			$('input[name="object-key"]').val('');

			// Generate widget HTML
			return lense.common.template.compile('object_widget', {
				widgetId:    widget_id,
				widgetKey:   k,
				widgetType:  widget_type,
				widgetLabel: widget_label
			});
		});

		/**
		 * Add Widget
		 */
		lense.common.object.registerHelper('manifest', 'addWidget', function(id, e) {
			var elem  = $(e);
			var id    = getattr(elem, 'widget');
			var label = getattr(elem, 'widget-label', id);
			var map   = getattr(elem, 'widget-map', false);

			// Unique widgets
			if ($('div[widget-id="' + id + '"]').length > 0) {
				return lense.common.layout.notify('danger', 'The ' + id + ' object is already defined!');
			}

			// Generate the widget
			return lense.common.template.compile('manifest_object', {
				id:    widget_id,
				type:  widget_id,
				widgetLabel: widget_label,
				widgetMap:   widget_map
			});
		});

	}

	/**
	 * Register Template Helpers
	 */
	this.registerTemplateHelpers = function() {

		/**
		 * Manifest Object
		 */
		Handlebars.registerHelper('manifestObject', function(id, type, key, map, opts) {

			// Optional attributes
			var key   = ((defined(key)) ? ' widget-key="' + key + '"': '');
			var map   = ((defined(map)) ? ' widget-map="' + map + '"': '');

			// Generated attributes
			var attrs = 'widget-id="' + id + '" widget-type="' + type + '"' + key + map;
			var grid  = 'data-gs-width="12" data-gs-height="1" data-gs-auto-position="true" data-gs-no-resize="true" ';

			// Return the HTML object
			return new Handlebars.SafeString(
				'<div class="grid-stack-item" ' + grid + attrs + '>' +
				'<x-var type="object">' +
				opts.fn(this) + '</x-var></div>');
		});

		/**
		 * Manifest Object Header
		 */
		Handlebars.registerHelper('manifestObjectHeader', function(type, key, opts) {
			var id = (defined(key)) ? type + '-' + key: type;
			return new Handlebars.SafeString('<h4 widget-id="' + id + '"></h4>');
		});

		/**
		 * Manifest Object Label
		 */
		Handlebars.registerHelper('manifestObjectLabel', function(id, label, key, opts) {
			var label = '<strong>' + label + '</strong>' + ((defined(key)) ? '#' + key: '');
			return new Handlebars.SafeString(
				'<div class="grid-stack-item-label">' +
				'<button type="button" class="btn btn-default btn-sm btn-gridstack-show-details" widget-id="' + id + '" data-toggle="collapse" data-target="#' + id + '-details">' + label + '</button>' +
				'</div>');
		});

		/**
		 * Manifest Object Variable
		 */
		Handlebars.registerHelper('manifestObjectVar', function(type, key, active, opts) {
			var type    = getattr(data, 'type');
			var key     = getattr(data, 'key');
			var id      = 'var-' + key;
			var display = getattr(data, 'active', false);

			var id      = 'var-' + key;
			var display = (active === 'true') ? 'block' : 'none';
			var state   = (active === 'true') ? '' : ' inactive';

			// Process variable type
			switch(type) {

				// Static variable
				case 'static':
					return new Handlebars.SafeString(
						'<div class="form-group var-type" var-type="' + type + '" widget-id="' + id + '" style="display:' + display + ';">' +
						'<label for="variable_static">Static:</label>' +
						'<input type="text" class="form-control var-' + type + '" placeholder="Static value..." widget-id="' + id + '">' +
						'<x-var type="str" key="var#' + key + '" value="input.var-' + type + '[widget-id=\'' + id + '\']"' + state + '>' +
						'</div>'
					);

				// Reference variable
				case 'ref':
					return new Handlebars.SafeString(
						'<div class="form-group var-type" var-type="' + type + '" widget-id="' + id + '" style="display:' + display + ';">' +
						'<label for="variable_reference">Reference:</label>' +
						'<div class="input-group">' +
						'<div class="input-group-addon">#</div>' +
						'<input type="text" class="form-control var-' + type + '"placeholder="varKey" widget-id="' + id + '">' +
						'<x-var type="str" key="var#'+ key + '" prefix="#" value="input.var-' + type + '[widget-id=\'' + id + '\']"' + state + '>' +
						'</div></div>'
					);

				// Commons variable
				case 'fetch':
					return new Handlebars.SafeString(
						'<div class="form-group var-type" var-type="' + type + '" widget-id="' + id + '" style="display:' + display + ';">' +
						'<label for="variable_reference">Commons Variable:</label>' +
						'<div class="input-group">' +
						'<div class="input-group-addon">LENSE.</div>' +
						'<input type="text" class="form-control var-' + type + '" placeholder="attrPath" widget-id="' + id + '">' +
						'<x-var type="object" key="var#' + key + '"' + state + '><x-var type="str" key="' + type + '" prefix="LENSE." value="input.var-' + type + '[widget-id=\'' + id + '\']"' + state + '></x-var>' +
						'</div></div>'
					);

				// Commons method
				case 'call':
				    break;

				// Invalid type
				default:
				    throw new Error('Invalid manifest variable type: ' + type);
			}
		});

	}

	/**
	 * Handler properties callback
	 *
	 * @param {Object} data Incoming response data
	 */
	lense.register.callback('loadHandler', function(data) {

		// Object source data
		self.object.setData(data);

		// Object header
		self.object.render('header');

		// Handler manifest
		self.object.renderGrid('content-center')('manifest', data, {
			extract: 'manifest'
		});

		// Handler properties
		self.object.render('content-right')(self.object.defineProperties(data, {
			exclude: ['manifest'],
			canEdit: ['name', 'path', 'method']
		}));
	});

	/**
	 * @constructor
	 */
	lense.register.constructor('admin.models', function() {

		// Load required object types
		self.object.require([
			'HandlerVariable',
			'HandlerAction',
			'HandlerParameters',
			'HandlerResponse'
		]);

		// Get handler details
		lense.api.request.submit('handler_get', {
			uuid: 'f71a6563-bfbf-469e-bf5e-386a5c573c52',
		}, 'loadHandler');
	});
});
