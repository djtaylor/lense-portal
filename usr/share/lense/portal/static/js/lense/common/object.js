lense.import('common.object', function() {
	var self = this;

	// Available grids
	this.grids   = [];

	// Helper methods
	this.helpers = {};

	/**
	 * Register Helper Method
	 */
	this.registerHelper = function(id, key, func) {
		if (!hasattr(self.helpers, id)) {
			self.helpers[id] = {};
		}
		self.helpers[id][key] = func;
	}

	/**
	 * Grid Interface
	 */
	this.grid = function(id) {
		var inner  = self.grids[id];
		var ref    = this;
		var source = lense.common.ace.editor(id);

		/**
		 * Get Helper
		 */
		this.helper = function(key) {
			return self.helpers[id][key];
		}

		/**
		 * Bind Initialize
		 */
		this.bindInit = function() {

			// Set keyed widget type in modal
			$(document).on('click', '.gridstack-add-keyed-widget', function() {
				$('#keyed-widget-type').val(getattr($(this), 'widget'));
			});

			// Add object widget
			$(document).on('click', '.gridstack-add-widget', function() {
				ref.addWidget(this, getattr($(this), 'widget-id'));
			});

			// Add keyed object widget
			$(document).on('click', '#gridstack-add-keyed-widget', function() {
				ref.addKeyedWidget(this, $('input[name="object-key"]').val());
			});

			// Remove widget
			$(document).on('click', '.gridstack-remove-widget', function() {
				ref.removeWidget(this);
			});

			// Edit widget
			$(document).on('click', '.gridstack-edit-widget', function() {
				var widget_id = getattr($(this), 'widget-id');

				// Toggle the widget attribute inspector
				$('.grid-stack-widget-attrs').css('display', 'none');
				$('.grid-stack-widget-attrs[widget-id="' + widget_id + '"]').css('display', 'block');
			});

			// Change variable type
			$(document).on('change', '#variable_type', function() {
				var value    = $(this).val();
				var id       = getattr($(this), 'widget-id');
				var all      = $('.var-type[widget-id="' + id + '"]');
				var selected = $('.var-type[widget-id="' + id + '"][var-type="' + value + '"]');

				// Toggle elements
				self.toggle(all, selected, function() {
					ref.resizeWidget(id);
				});
			});

			// Change variable args type
			$(document).on('change', '#variable_call_args_type', function() {
				var value    = $(this).val();
				var id       = getattr($(this), 'widget-id');
				var all      = $('.args-type[widget-id="' + id + '"]');
				var selected = $('.args-type[widget-id="' + id + '"][args-type="' + value + '"]');

				// Toggle elements
				self.toggle(all, selected, function() {
					ref.resizeWidget(id);
				});
			});

			// Change variable kwargs type
			$(document).on('change', '#variable_call_kwargs_type', function() {
				var value    = $(this).val();
				var id       = getattr($(this), 'widget-id');
				var all      = $('.kwargs-type[widget-id="' + id + '"]');
				var selected = $('.kwargs-type[widget-id="' + id + '"][kwargs-type="' + value + '"]');

				// Toggle elements
				self.toggle(all, selected, function() {
					self.resizeWidget(id);
				});
			});

			// Show widget details
			$(document).on('shown.bs.collapse', '.widget-collapse', function() {
				ref.resizeWidget(getattr($(this), 'widget-id'));
			});

			// Hide widget details
			$(document).on('hidden.bs.collapse', '.widget-collapse', function() {
				ref.collapseWidget(getattr($(this), 'widget-id'));
			});

			// Add method argument
			$(document).on('click', '.btn-add-args', function() {
				var id    = getattr($(this), 'widget-id');
			});

			// Change variable key
			$(document).on('input', '.widget-key-value', function() {
				var id    = getattr($(this), 'widget-id');
				var key   = $(this).val();
				var type  = getattr($(this), 'widget-type');
				ref.updateKey(id, type, key);
			});

			// Add method keyword argument
			$(document).on('click', '.btn-add-kwarg', function() {
				var id    = getattr($(this), 'widget-id');

				// Add the keyword argument
				lense.common.template.render('div[widget-id="' + id + '"][var-type="kwargs"]', 'object_var_kwarg', {
					widgetId: id
				}, {
					flush: false
				});

				// Resize the widget container
				ref.resizeWidget(getattr($(this), 'widget-id'));
			});

			// Remove method keyword argument
			$(document).on('click', '.btn-remove-widget-attr', function() {
				var uuid = getattr($(this), 'widget-uuid');
				$('.widget-attr-row[widget-uuid="' + uuid + '"]').remove();

				// Resize the widget container
				ref.resizeWidget(getattr($(this), 'widget-id'));
			});

			// Add method argument
			$(document).on('click', '.btn-add-arg', function() {
				var id    = getattr($(this), 'widget-id');

				// Add the keyword argument
				lense.common.template.render('div[widget-id="' + id + '"][var-type="args"]', 'object_var_arg', {
					widgetId: id
				}, {
					flush: false
				});

				// Resize the widget container
				ref.resizeWidget(getattr($(this), 'widget-id'));
			});

			// View source / grid
			$.each(['view-grid[object="' + id + '"]', 'view-grid-source[object="' + id + '"]'], function(i,e) {
				$(document).on('click', '#' + e, function() {
					lense.common.layout.swap('#' + id + '-grid', '#' + id + '-source');
					lense.common.layout.swap('#view-grid-source[object="' + id + '"]', '#view-grid[object="' + id + '"]');
				});
			});

			// Refresh bind
			ref.bindRefresh();
		}

		/**
		 * Bind Refresh
		 */
		this.bindRefresh = function() {
			$.each(['input', 'select', 'textarea'], function(i,type) {
				$.each($('x-var[id="' + id + '"]').find(type), function(i,elem) {
					$.each(['input', 'change'], function(i,event) {
						$(document).on(event, elem, function() {
							ref.updateSource();
						});
					});
				});
			});
		}

		/**
		 * Update Source
		 */
		this.updateSource = function() {
			console.log('update source');
			source.setValue(JSON.stringify(self.collectData(id), null, 2));
		}

		/**
		 * Update Widget Key
		 */
		this.updateKey = function(widget_id, widget_type, widget_key) {
			$('.btn-gridstack-show-details[widget-id="' + widget_id + '"]').html('<strong>' + widget_type + '</strong>#' + widget_key);
			$('[widget-id="' + widget_id + '"]').attr('widget-id', widget_type + '#' + widget_key);

			// Update source
			ref.updateSource();
		}

		/**
		 * Resize Widget
		 */
		this.resizeWidget = function(widget_id) {
			var height = $('.widget-collapse[widget-id="' + widget_id + '"]').actual('height');
			var ysize  = Math.ceil(height / 40);

			// Resize the widget
			inner.data('gridstack').resize('.grid-stack-item[widget-id="' + id + '"]', null, ysize);
		}

		/**
		 * Collapse Widget
		 */
		this.collapseWidget = function(widget_id) {
			inner.data('gridstack').resize('.grid-stack-item[widget-id="' + widget_id + '"]', null, 1);
		}

		/**
		 * Remove Widget
		 */
		this.removeWidget = function(e) {

			// Widget ID
			var widget_id = getattr($(e), 'widget-id');

			// Remove the grid item
			inner.data('gridstack').removeWidget('.grid-stack-item[widget-id="' + widget_id + '"]');

			// Remove attributes inspector
			lense.common.layout.remove('.grid-stack-widget-attrs[widget-id="' + widget_id + '"]');

			// Update source
			ref.updateSource();
		}

		/**
		 * Add Widget Attributes Inspector
		 */
		this.addWidgetInspector = function(attrs) {
			var inspector_id = getattr(attrs, 'id');
			lense.common.template.render('#' + inspector_id + '-details', 'object_widget_attrs', {
				widgetId: inspector_id,
				widgetType: getattr(attrs, 'type', attrs['id']),
				widgetKey: getattr(attrs, 'key', null)
			});
		}

		/**
		 * Add Keyed Widget
		 */
		this.addKeyedWidget = function(elem,key,widget) {

			// Create the widget
			inner.data('gridstack').addWidget(ref.helper('addKeyedWidget')(id, e));

			// Create the widget inspector
			ref.addWidgetInspector({ id: widget_id, type: widget_type, key: k});

			// Rebind
			ref.bindRefresh();

			// Update source
			ref.updateSource();
		}

		/**
		 * Add Widget
		 */
		this.addWidget = function(elem,widget) {

			// Create the widget
			inner.data('gridstack').addWidget(ref.helper('addWidget')(id, e));

			// Create the widget inspector
			ref.addWidgetInspector({ id: widget });

			// Rebind
			ref.bindRefresh();

			// Update source
			ref.updateSource();
		}

	}

	/**
	 * Bootstrap Object Interface
	 */
	this.bootstrap = function(id, data, options) {
		$(document).ready(function() {

			// Define the grid
			self.grids[id] = $('#' + id + '-grid');

			// Setup the grid
			self.grids[id].gridstack(options);

			// Grid source editor
			lense.common.ace.setup(id, id + '-source', {
				data: data
			});
		});

		// Object interface
		var object = new self.grid(id);

		// Bind events
		object.bindInit();

		// Return object interface
		return object;
	}

	/**
	 * Clear Object Field Value
	 */
	this.clearFieldValue = function(e) {
		var elem  = $(e);
		var attrs = get_attr(elem);

		// Reset to the default value
		elem.val(attrs.defval);
	}

	/**
	 * Toggled Data Objects / Containers
	 */
	this.toggle = function(disabled,enabled,callback) {

		// Hide/disable nested variables
		disabled.css('display', 'none');
		$.each(disabled.find('x-var'), function(i,e) {
			$(e).attr('inactive', true);
		});

		// Show / enable active variables
		enabled.css('display', 'block');
		$.each(enabled.find('x-var'), function(i,e) {
			$(e).removeAttr('inactive');
		});

		// Callback
		if (defined(callback)) {
			callback();
		}
	}

	/**
	 * Create Object
	 */
	this.create = function() {
		var request = get_attr($('#create-object-request'));
		var attrs   = request.attrs.split(',');
		var data    = self.createData(attrs);
		console.log(data);
		self.clearData(attrs);
	}

	/**
	 * Bind Events
	 */
	this.bind = function() {

		// Create object
		$(document).on('click', '#create-object-submit', function() {
			self.create();
		});
	}

	// Objects / source containers
	this.objects = {};
	this.sources = {};

	/**
	 * Source Interface
	 */
	this.SourceInterface = function(id, opts) {
		return lense.common.ace.editor(id);
	}

	/**
	 * Object Interface
	 */
	this.ObjectInterface = function(id, opts) {
		var inner    = this;

		// Widgets / grids
		this.widgets = {};
		this.grids   = {};

		// Define source interface
		self.sources[id] = new self.SourceInterface(id, opts);
		this.source      = self.sources[id];

		/**
		 * Bootstrap Object Interface
		 */
		this.bootstrap = function(opts) {
			var data = getattr(opts, 'data');
			console.log(data);
		}

		/**
		 * Define Object Structure
		 */
		this.structure = function(structure) {

		}

		/**
		 * Define Grid
		 */
		this.defineGrid = function(grid) {

		}

		/**
		 * Define Widget
		 */
		this.defineWidget = function(widget, constructor) {}

		/**
		 * @constructor
		 *
		(function() {
			$(document).ready(function() {
				inner.defineGrid(id);

				// Define the grid
				self.grids[id] = $('#' + id + '-grid');

				// Setup the grid
				self.grids[id].gridstack({
					cellHeight: 40,
			        verticalMargin: 10,
			        draggable: {
			            handle: '.move-widget[grid-id="' + id + '"]'
			        }
				});

				// Grid source editor
				lense.common.ace.setup(id, id + '-source', {
					data: data
				});
			});

			// Object interface
			var object = new self.grid(id);

			// Bind events
			object.bindInit();

			// Return object interface
			return object;
		})();
		*/
	}

	/**
	 * Define New Object
	 */
	this.define = function(id, opts) {
		self.objects[id] = new self.ObjectInterface(id, opts);
		return self.objects[id];
	}

	/**
	 * Constructor
	 */
	lense.register.constructor('common.object', function() {
		self.bind();
	});
});
