lense.import('object.interface', function() {
	var self     = this;

	// Objects / source containers
	this.objects = {};

	/**
	 * Initialize Interface
	 * @constructor
	 */
	this.__init__ = function() {
		lense.implement([
		    'object.library'
		]);

		// Custom x-var selector
		$.expr[':'].activeVar = function(a) {
			return $(a).is(':hidden') && $(a).css('display') != 'none';
		};

		// Object key modal shown
		$(document).on('shown.bs.modal', '#object-key', function() {
      $('input[name="object-key"]').focus();
    });

		// Delete object modal
		$(document).on('show.bs.modal', '#object-delete', function() {
			var target = $('input[uuid]:visible:checked').val();
			if (!defined(target)) {
				lense.log.warn('Must select an object to delete!');
				return false;
			}
			$('#object-delete-header').text('Confirm Delete: ' + target);
			$('#object-delete-submit').attr('uuid', target);
			return true;
		});

		// Object key modal hidden
		$(document).on('hidden.bs.modal', '#object-key', function() { });

		// Layout preference
		self.setLayout(lense.preferences.get('layout', 'list'));
	}

	/**
	 * Set the layout for list/thumbnail overview
	 *
	 * @param {String} layout The layout type to show
	 */
	this.setLayout = function(layout) {

		// Clear active state and hide all
		$('button[object-toggle-layout]').removeClass('active');
		$('div[object-layout]').css('display', 'none');

		// Set new active state and show target layout
		$('button[object-toggle-layout="' + layout + '"]').addClass('active');
		$('div[object-layout="' + layout + '"]').css('display', 'block');

		// Store the preference
		lense.preferences.set('layout', layout);
	}

	/**
	 * Check if variable is inactive
	 *
	 * @param {Object} e The jQuery element selector
	 */
	this.isInactive = function(e) {
		return ((getattr(e, 'inactive', false) === false) ? false:true);
	}

	/**
	 * Get variable type
	 *
	 * @param {Object} e The jQuery element selector
	 */
	this.getType = function(e) {
		var type = getattr(e, 'type');
		if ($.inArray(type, ['str', 'int', 'bool', 'array', 'object']) == -1) {
			throw new Error('Invalid variable type: ' + type);
		}
		return type;
	}

	/**
	 * Get default value attribute
	 */
	this.getDefault = function(e) {
		var def = getattr(e, 'default', false);
		if (def !== false) {
			switch(def) {
				case "null":
					return null;
				case "false":
					return false;
				case "true":
					return true;
				default:
					return def;
			}
		} else {
			return undefined;
		}
	}

	/**
	 * Get variable value
	 *
	 * @param {Object} e The jQuery element selector
	 */
	this.getValue = function(e) {
		var is_static = e.attr('static');
		var type      = getattr(e, 'type');
		var prefix    = getattr(e, 'prefix', '');
		var suffix    = getattr(e, 'suffix', '');
		var value     = (function() {
			if (type === 'bool') {
				return ($(getattr(e, 'value')).is(':checked')) ? true:false;
			} else if (typeof is_static !== typeof undefined && is_static !== false) {
				return getattr(e, 'value');
			} else {
				return $(getattr(e, 'value')).val();
			}
		}());

		// Return value
		if (type === 'bool') {
			return value;
		} else {
			return (defined(value)) ? prefix + value + suffix:false;
		}
	}

	/**
	 * Walk through data structure
	 *
	 * @param {Object} parent The parent element
	 * @param {Object} ref The referenced data object to construct
	 */
	this.constructData = function(parent, ref) {
		$.each(parent.children(), function(i,e) {
			var elem = $(e);
			if (elem.is('x-var')) {
				var type = self.getType(elem);
				var def  = self.getDefault(elem);
				var key  = (function() {
					var keyval = getattr(elem, 'key', false);

					// No key found
					if (keyval === false) {
						return false;
					} else {

						// Dynamic key value
						if (keyval.startsWith('@')) {
							return $(keyval.slice(1)).val();

						// Static key value
						} else {
							return keyval;
						}
					}
				}());

				// Element is inactive
				if (self.isInactive(elem)) {
					return true;
				}

				// Parent data is array
				if ($.isArray(ref)) {
					if (key !== false) {
						throw new Error('Parent array cannot contain keyed element');
					}

					// Childless elements
					if ($.inArray(type, ['str', 'int', 'bool']) !== -1) {
						var value = self.getValue(elem);

						// Not defined and default present
						if (!defined(value) && def !== undefined) {
							value = def;
						}

						// Boolean value
						if (type == 'bool') {
							ref.push(value);

						// Other value
						} else {
							if (value !== false) {
								ref.push(value);
							}
						}
					} else {
						ref.push(((type === 'array') ? []: {}));
						self.constructData(elem, ref[ref.length - 1]);
					}

				// Assume object
				} else {
					if (key === false) {
						throw new Error('Parent object cannot contain un-keyed element')
					}

					// Key already defined
					if (key in ref) {
						throw new Error('Parent object contains duplicate key: ' + key);
					}

					// Childless elements
					if ($.inArray(type, ['str', 'int', 'bool']) !== -1) {
						var value = self.getValue(elem);

						// Not defined and default present
						if (!defined(value) && def !== undefined) {
							value = def;
						}

						// Boolean value
						if (type == 'bool') {
							ref[key] = value;

						// Other value
						} else {
							if (value !== false) {
								ref[key] = value;
							}
						}
					} else {
						ref[key] = ((type === 'array') ? []: {});
						self.constructData(elem, ref[key]);
					}
				}
			} else {
				self.constructData(elem, ref);
			}
		});
	}

	/**
	 * Collect object data
	 *
	 * @param {String} id The ID of the parent variable object
	 */
	this.collectData = function() {
		var top   = $('x-var[id="object-data"]');
		var type  = self.getType(top);
		var data  = (function() {
			switch(type) {
				case 'str':
				case 'bool':
				case 'int':
					return self.getValue(top);
					break;
				case 'array':
					return [];
					break;
				case 'object':
					return {};
					break;
				default:
					return null;
			}
		})();

		// Top level element has no children
		if ($.inArray(type, ['str', 'int', 'bool']) !== -1) {
			return data;
		}

		// Construct data object
		try {
			self.constructData(top, data);
		} catch(e) {
			lense.log.warn(e);
			return undefined;
		}

		// Return data
		return data;
	}

	/**
	 * Base interface object
	 *
	 * @param {String} id A unique interface ID, i.e., data, object, source
	 * @param {Object} child The child object
	 */
	function BaseInterface(id, child) {
		lense.log.debug('Bootstrapping interface: ' + id);

		// Child attributes
		this.id    = id;

		// Extend child interface
		return extend(child, this);
	}

	/**
	 * Data interface
	 *
	 * @param {Object} data The data object
	 */
	function DataInterface(data) {
		var local    = new BaseInterface('data', this);

		// Local data
		local.object = clone(data);

		/**
		 * Return a hash of data
		 */
		local.hash = function() {
			return local.object;
		}

		/**
		 * Get data element
		 *
		 * @param {String} selector The selector object
		 * @param {*} def The default to return if key not found
		 */
		local.get = function(selector, def) {

			// Select from an array of data
			if (istype(selector, 'array')) {
				var retval = def;
				$.each(local.object, function(i, obj) {
					if (obj[selector[0]] == selector[1]) {
						retval = obj;
					}
				});
				return retval;

			// Select key from a single data object
			} else {
				return getattr(local.object, selector, def);
			}

			if (istype(local.object, 'array')) {

			}
			return getattr(local.object, key, def)
		}

		/**
		 * Iterate through data
		 *
		 * @param {Function} callback The iteration callback
		 */
		local.each = function(callback) {

			// Array of objects
			if (istype(local.object, 'array')) {
				$.each(local.object, function(i,obj) {
					return callback(i,obj);
				});

			// Single object
			} else {
				$.each(local.object, function(k,obj) {
					return callback(k,obj);
				});
			}
		}

		// Return the data interface
		return local
	}

	/**
	 * Source interface
	 *
	 * @param {Object} data The object data
	 * @param {Object} opts Any additional options
	 */
	function SourceInterface(data, opts) {
		var local = new BaseInterface('source', this);

		// Define the editor
		local.editStartor = ace.edit('object-source');

		// Theme / mode
		local.editor.setTheme(getattr(opts, 'theme', 'ace/theme/chrome'));
		local.editor.getSession().setMode(getattr(opts, 'mode', 'ace/mode/json'));

		// Read only (editing not supported)
		local.editor.setReadOnly(getattr(opts, 'readOnly', true));

		// Autosize editor window
		local.editor.$blockScrolling = Infinity;
		local.editor.setOptions({
			maxLines: Infinity
		});

		// If data provided
		if (defined(data)) {
			local.editor.setValue(JSON.stringify(data, undefined, 2), -1);
		}

		/**
		 * Update source code
		 *
		 * @param {Object} source The source object to render
		 */
		local.update = function(source) {
			local.editor.setValue(JSON.stringify(source, undefined, 2), -1);
		}

		// Return the source interface
		return local;
	}

	/**
	 * Object Interface
	 *
	 * @param {String} uuid The object UUID
	 * @param {String}
	 */
	function ObjectInterface(uuid, type) {
		var local = new BaseInterface('object', this);
		var inner = this;

		// Options / grids / properties
		local.opts, local.grids, local.template, local.properties, local.source, local.data;

		// UUID and type
		local.uuid   = uuid;
		local.type   = type;

		// Create flag and checks
		local.create = (function() {
			var create = lense.url.getParam('create', false);
			if (create && local.uuid) {
				lense.raise('UUID and create parameters not compatible!');
			}
			return create;
		}());

		// Edit flag and checks
		local.edit   = (function() {
			var edit = lense.url.getParam('edit', false);
			if (edit && local.create) {
				lense.raise('Create and edit parameters not compatible!');
			}
			if (!defined(local.uuid)) {
				lense.raise('Cannot edit with selecting an object!');
			}
			return edit;
		}());

		// Set the view
		local.view   = ((!local.uuid && !local.create) ? 'list':'object');

		/**
		 * Set object options
		 *
		 * @param {Object} opts Object interface options
		 */
		local.setOptions = function(opts) {
			local.opts = opts;
		}

		/**
		 * Define data template object
		 *
		 * @param {OrderedObject} template The object data template
		 */
		local.defineTemplate = function(template) {
			if (!template.name === 'OrderedObject') {
				lense.raise('Object template must be an instance of "OrderedObject"!');
			}
			local.template = template;
		}

		/**
		 * Define positional properties object
		 *
		 * @param {String} pos The position to render
		 * @param {Object} filter The positional properties filter
		 */
		local.defineProperties = function(pos, filter) {
			var exclude = getattr(filter, 'exclude', false);
			var include = getattr(filter, 'include', false);
			var render  = new OrderedObject();

			// Include/exclude mutually exclusive
			if (exclude && include) {
				lense.raise('Exclude and include filter options not compatible for properties: ' + pos);
			}

			// Including specific attributes
			if (include) {
				local.template.each(function(k,v) {
					if ($.inArray(k, include)) {
						render.append(k,v);
					}
				});
			}

			// Excluding specific attributes
			if (exclude) {
				local.template.each(function(k,v) {
					if (!$.inArray(k, exclude)) {
						render.append(k,v);
					}
				});
			}

			// Store the properties
			local.properties[pos] = render;
		}

		/**
		 * Define grid object
		 *
		 * @param {String} pos The grid position
		 * @param {String} key The grid parent data key
		 * @param {Array} require A list of grid object templates to require
		 */
		this.defineGrid = function(pos, opts) {
			var gridOpts = local.template.get(key);

			// Key must be in template
			if (!defined(gridOpts)) {
				lense.raise('Grid key "' + key + '" not found in object template!');
			}

			// Key must set grid=true
			if (!getattr(gridOpts, 'grid', false)) {
				lense.raise('Grid key "' + key + '" must have "grid" attribute set to: true!');
			}

			// Grid object types
			$.each(getattr(opts, 'require', []), function(i,t) {
				getattr(lense.object.library, t).setup();
			});

			// Store the grid key
			local.grids[pos] = getattr(opts, 'key');
		}

		/**
		 * @constructor
		 */
		local.__init__ = function() {

			// Set view state
			$.each(['list', 'object'], function(i,key) {
				$('div[view="' + key + '"]').css('display', ((local.view == key) ? 'block':'none'));
			});

			// Toggle button states
			$(document).on('click', 'button[btn-toggle*="#"]', function() {
				var view   = $(this).attr('view');
				var group  = view.split('#')[0];
				var target = view.split('#')[1];
				$.each($('button[btn-toggle*="' + group +'#"]'), function(i,e) {
					var elem = e;
					elem.css('display', (function() {
						if (elem.css('display') === 'none') {
							return getattr(elem, 'btn-display', 'block');
						}
						return 'none';
					}()));
				});
			});
		}

		/**
		 * Set object constructor method
		 *
		 * @param {Object} func The constructor method
		 */
		local.constructObject = function(func) {
			local.construct.object = func;
		}

		/**
		 * Set object list constructor method
		 *
		 * @param {Object} func The constructor method
		 */
		local.constructList = function(func) {
			local.construct.list = func;
		}

		/**
		 * Edit state start
		 */
		local.editStart = function() {

			// Enable editable elements and buttons
			$('[edit][disabled]').removeAttr('disabled');

			// Toggle buttons
			$('#edit-object').css('display', 'none');
			$('#save-object').css('display', 'inline-block');
			$('#edit-object-cancel').css('display', 'inline-block');
		}

		/**
		 * Bind events
		 */
		local._bind = function() {

			// Update source
			$.each(['input', 'blur', 'change', 'select'], function(i,e) {
				$(document).on(e, '[update-source]', function() {
					var data = self.collectData();
					if (!defined(data)) {
						lense.log.debug('Failed to update source: data undefined');
						return false;
					}
					self.source.update(data);
				});
			});

			// Edit object
			$(document).on('click', '#edit-object', function() {
				lense.url.setParam('edit', true);
				local.editStart();
			});

			// Save object
			$(document).on('click', '#save-object', function() {
				console.log(lense.object.collectData('object-data'));
			});

			// Cancel edit
			$(document).on('click', '#edit-object-cancel', function() {
				window.location.href = window.location.pathname + '?view=' + lense.url.getParam('view') + '&uuid=' + lense.url.getParam('uuid');
			});

			// Change list layout
			$(document).on('click', 'button[object-toggle-layout]', function() {
				self.setLayout(getattr($(this), 'object-toggle-layout'));
			});

			// Disable the selected group
			$(document).on('click', 'button.active[object-toggle-target]', function() {

			});

			// Add argument
			$(document).on('click', 'button[object-var-add="list"]', function() {
				var oid  = getattr($(this), 'object-id');
				var html = $(Handlebars.helpers.object_var_arg(oid, null).string).find('[disabled]').removeAttr('disabled');
				var elem = $('x-var[object-id="' + oid + '"][key="args"]');

				// Add a new argument
				elem.append(html[0].outerHTML);

				// Resize details
				local.resizeDetails(oid);
			});

			// Add keyword argument
			$(document).on('click', 'button[object-var-add="dict"]', function() {
				var oid  = getattr($(this), 'object-id');
				var key  = getattr($(this), 'object-key', 'kwargs');
				var html = $(Handlebars.helpers.object_var_kwarg(oid, null, null).string).find('[disabled]').removeAttr('disabled');
				var elem = $('x-var[object-id="' + oid + '"][key="' + key + '"]');

				// Add a new keyword argument
				elem.append(html[0].outerHTML);

				// Resize details
				local.resizeDetails(oid);
			});

			// Remove argument
			$(document).on('click', '.btn-remove-object-attr', function() {
				var uuid = getattr($(this), 'uuid');
				var oid  = getattr($(this), 'object-id');
				$('.object-attr-row[uuid="' + uuid + '"]').remove();
				local.resizeDetails(oid);
			});

			// Show object details
			$(document).on('shown.bs.collapse', '.object-collapse', function() {
				var oid = getattr($(this), 'object-id');
				local.resizeDetails(oid);
			});

			// Hide widget details
			$(document).on('hidden.bs.collapse', '.object-collapse', function() {
				var oid = getattr($(this), 'object-id');
				local.collapseDetails(oid);
			});

			// Data groups
			$(document).on('click', 'button[data-group]', function() {
				var group    = getattr($(this), 'data-group');
				var target   = getattr($(this), 'data-target');
				var oid      = getattr($(this), 'object-id');

				// All group objects
				var all      = {
					buttons: $('button[data-group="' + group + '"]'),
					children: $('div[data-parent="' + group + '"]')
				};

				// Selected objects
				var selected = {
					button: $('button[data-group="' + group + '"][data-target="' + target + '"]'),
					children: $('div[data-parent="' + group + '"][data-element="' + target + '"]')
				};

				// Disable group
				if ($(this).hasClass('active')) {
					selected.button.removeClass('active');
					selected.children.css('display', 'none');
					selected.children.find('x-var').attr('inactive', '');

				// Switch groups
				} else {

					// Disable all buttons / children
					all.buttons.removeClass('active');
					all.children.css('display', 'none');
					all.children.find('x-var').attr('inactive', '');

					// Enable selected button / children
					selected.button.addClass('active');
					selected.children.css('display', 'block');
					selected.children.find('x-var').removeAttr('inactive');
				}

				// Resize widget
				local.resizeDetails(oid);

				// Update source
				if (hasattr($(this), 'update-source')) {
					local.source.update(lense.object.collectData('object-data'));
				}
			});
		}

		/**
		 * Expand object details
		 *
		 * @param {String} id The object ID
		 */
		local.resizeDetails = function(id) {
			var height = $('.object-collapse[object-id="' + id + '"]').actual('height');
			var ysize  = Math.ceil(height / 40);

			// Resize the widget
			local.grid.data('gridstack').resize('.grid-stack-item[object-id="' + id + '"]', null, (ysize == 1) ? 2: ysize);
		}

		/**
		 * Collapse object details
		 *
		 * @param {String} id The object ID
		 */
		local.collapseDetails = function(id) {
			local.grid.data('gridstack').resize('.grid-stack-item[object-id="' + id + '"]', null, 1);
		}

		/**
		 * Set source data.
		 *
		 * @param {Object} data The object source data
		 * @param {Object} options Any additional options
		 * @param {Array} options.filter Attributes to filter from source data
		 */
		local.setData = function(data, options) {
			var filter  = getattr(options, 'filter', []);
			self.data   = new DataInterface(id, data);
			self.source = new SourceInterface(id, (function() {
				var copy = clone(self.data.object);
				$.each(filter, function(i,key) {
					delete copy[key];
				});
				return copy;
			}()));
		}

		/**
		 * Create a new grid object.
		 *
		 * @param {String} id The grid ID
		 * @param {String} type The grid object type
		 * @param {String} key The grid object key
		 * @param {Object} attrs The grid object attributes
		 */
		local.createGridObject = function(id, type, key, attrs) {
			try {
				lense.object.library.mapType(type).create(local.grid, key, attrs);
			} catch (e) {
				lense.log.warn(e);
			}
		}

		/**
		 * Convert source object to grid layout.
		 *
		 * @param {String} id The grid ID
		 * @param {Object} data Grid data objects
		 */
		local.sourceToGrid = function(id, data) {
			if ($.isArray(data)) {
				$.each(data, function(i,o) {
					$.each(o, function(item,attrs) {
						var type = (item.indexOf('#') >= 0) ? item.split('#')[0]:item;
						var key  = (item.indexOf('#') >= 0) ? item.split('#')[1]:null;
						local.createGridObject(id, type, key, attrs);
					});
				});
			} else {
				lense.log.warn('Grid data must be an array!');
			}
		}

		/**
		 * Bootstrap grid editor
		 *
		 * @param {String} pos The grid position
		 * @param {String} key The grid key
		 * @param {Object} data Grid data
		 */
		local.bootstrapGrid = function(pos, key, data) {
			var id = 'grid-' + key;

			// Create the grid container
			$('#object-' + loc).html(
				'<x-var type="array" key="' + key + '">' +
				'<div id="' + id + '"></div>' +
				'</x-var>'
			);

			// Define the grid
			var grid = $('#' + id);

		}

		/**
		 * Render a grid editor.
		 *
		 * @param {String} loc The grid location
		 * @returns {Function}
		 */
		 local.renderGrid = function(loc) {
			 switch(loc) {
				 case "content-left":
				 case "content-right":
				 case "content-center":
				 	 return function(id, data, opts) {

						 // Grid already defined
						 if (defined(local.grid)) {
							 lense.log.warn('Can only define one grid per object!');
							 return false;
						 }

						 // Create the grid container / source editor
						 $('#object-' + loc).html(
							 '<x-var type="array" key="' + id + '">' +
							 '<div class="grid-stack" object-grid="' + id + '"></div>' +
							 '</x-var>'
						 );

						 // Define the grid
						 local.grid = $('div[object-grid="' + id + '"]');

						 // Setup the grid
						 local.grid.gridstack({
							 cellHeight: 40,
									 verticalMargin: 10,
									 draggable: {
											 handle: '.object-move'
									 }
						 });

						 // Set to static unless editing
						 local.grid.data('gridstack').setStatic(true);

						 // Render data
						 if (defined(data)) {
							 var extract = getattr(opts, 'extract', false);

							 // Convert source to grid
							 local.sourceToGrid(id, (extract !== false) ? data[extract]:data);
						 }

						 // Remove widget
			 			$(document).on('click', '.object-remove', function(i,e) {
							local.grid.data('gridstack').removeWidget('div[object-id="' + getattr($(this), 'object-id') + '"]');
			 			});
					 }
				 	 break;
				 default:
					 lense.log.warn('Invalid layout location: ' + loc);
			 }
		 }

		/**
		 * Bootstrap property fields
		 *
		 * @param {Object} template The local template for this position
		 */
		local.bootstrapProperties = function(template) {
			var fields = [];
			template.each(function(key, attrs) {
				fields.push(Handlebars.helpers.object_property(key, local.data.get(key), attrs));
			});
			return fields.join('');
		}

		/**
		 * Bootstrap list controls
		 */
		local.bootstrapListControls = function() {
			return Handlebars.helpers.manage_objects().string;
		}

		/**
		 * Bootstrap sort controls
		 */
		local.bootstrapSortControls = function() {
			return Handlebars.helpers.sort_objects(local.template).string
		}

		/**
		 * Bootstrap the object header
		 */
		local.bootstrapHeader = function() {
			if (defined(local.uuid)) {
				return '<h4>' + local.type + '::' + local.uuid + '</h4>';
			} else if (local.create) {
				return '<h4>' + local.type + '::CREATE</h4>';
			} else {
				return '<h4>' + local.type + 's</h4>'
			}
		}

		/**
		 * Bootstrap the object thumbnails layout
		 */
		local.bootstrapThumbnails = function () {
			var thumbnails = [];
			$.each(local.data.hash(), function(i,object) {
				thumbnails.push(Handlebars.helpers.object_thumbnail(object, properties, opts));
			});
			return thumbnails.join('');
		}

		/**
		 * Bootstrap the object rows layout
		 */
		local.bootstrapRows = function() {
			var headers = Handlebars.helpers.object_headers(local.template);
			var rows    = [];

			// Process data
			local.data.each(function(i,object) {
				rows.push(Handlebars.helpers.object_row(object, local.template));
			});

			// Render headers
			$('#object-rows-headers').html(headers.string);

			// Return rows
			return rows.join('');
		}

		/**
		 * Render worker
		 *
		 * @param {String} pos The position to render to
		 */
		local.render = function(pos) {

			// Render worker
			function worker(html, flush) {
				$('#object-' + pos)[(flush ? 'html':'append')](html);
			}

			// Check visibility
			function visible() {
				return ($('#object-' + pos).css('display') == 'none') ? false:true;
			}

			// Size content columns
			function sizeColumns() {
				$('#object-' + loc).css('display', 'inline-block');
				var isVisible = [];
				$.each(['content-left', 'content-center', 'content-right'], function(i,current) {
					if (current != 'content-center') {
						visible(current) ? isVisible.push(current):null;
					}
				});

				// Resize center column
				$('#object-content-center').attr('class', 'col-md-' + (12 - (isVisible.length * 4).toString());
			}

			// Process location
			switch(pos) {
				case "content-left":
				case "content-center":
				case "content-right":
					sizeColumns(pos);
				case "header":
				case "list-controls":
				case "rows-body":
				case "list-thumbnails":
				case "footer":
				case "controls-create":
				 return worker
				 break;
				default:
				 lense.raise('Invalid render position: ' + pos);
			 }
		}

		/**
		 * Interface constructor
		 */
		local.construct = function() {

			// Render the object header
			local.render('header')(local.bootstrapHeader());

			// Construct based on the current view
			switch(local.view) {
				case "list":

					// List controls / sorting manager
					local.render('list-controls')(local.bootstrapListControls());
					local.render('sort')(local.bootstrapSortControls());

					// Construct the object list / thumbnail layouts
					local.render('list-rows')(local.bootstrapRows());
					local.render('list-thumbnails')(local.bootstrapThumbnails());

					break;
				case "object":

					// Construct source view
					local.source = new SourceInterface(local.data.hash());

					// Construct grids
					$.each(local.grids, function(pos, attrs) {
						local.render(pos)(local.bootstrapGrid(pos, attrs.key, data[attrs.key]));
					});

					// Construct properties
					$.each(local.properties, function(pos, attrs) {
						local.render(pos)(local.bootstrapProperties(attrs));
					});

					break;
				default:
					lense.raise('Cannot construct interface, invalid view: ' + view);
			}
		}

		 /**
		  * Callback for response data
			*/
    lense.register.callback('objectResponse', function(data) {

			// Setup the data interface
			local.data = new DataInterface(data);

		  // Construct the view
			local.construct();
		});

		 /**
 		 * Bootstrap the object
 		 */
 		local.bootstrap = function() {

 			// Creating an object
 			if (local.create) {
 				return lense.callback['objectResponse'](local.properties.hash());
 			}

 			// Get objects and pass to callback
 			lense.api.request.submit(getattr(local.opts.handler, 'get'), {
 				uuid: local.uuid,
 			}, 'objectResponse')
 		}

		// Return object interface
		return local;
	}

	/**
	 * Define a new object interface
	 *
	 * @param {String} type The object type
	 * @param {String} uuid The object UUID if loading an existing object
	 * @param {Object} opts Any additional options
	 * @returns {ObjectInterface}
	 */
	this.define = function(type, uuid) {
		var uuid   = (!defined(uuid) ? lense.url.getParam('uuid', false):uuid);
		var object = new ObjectInterface(uuid, type);

		// Initialize the object
		if (hasattr(object, '__init__')) {
			object.__init__();
		}

		// Store / return the object
		self.objects[id] = object;
		return object;
	}
});

// Register object list constructor method
self.object.constructList(function(data) {

	// Object header
	self.object.render('header');

	// List controls
	self.object.render('list-controls')(properties);

	// List objects (rows)
	self.object.render('rows-body')(self.object.defineRows(data, properties));

	// List objects (thumbnails)
	self.object.render('list-thumbnails')(self.object.defineThumbnails(data, properties, {
		title: 'name'
	}));
});

// Register single object constructor method
self.object.constructObject(function(data) {

	// Object source data
	self.object.setData(data, {
		filter: ['id']
	});

	// Object header
	self.object.render('header');

	// Handler manifest
	self.object.renderGrid('content-center')('manifest', data, {
		extract: 'manifest'
	});

	// Handler properties
	self.object.render('content-right')(self.object.defineProperties(data, {
		name: {
			edit: true
		},
		uuid: {
			label: 'UUID'
		},
		desc: {
			edit: true,
			label: 'Description'
		},
		path: {
			edit: true
		},
		method: {
			type: 'select',
			options: ['GET', 'PUT', 'POST', 'DELETE'],
			edit: true
		},
		enabled: {
			type: 'bool',
			edit: true
		},
		protected: {
			type: 'bool',
			edit: true
		},
		allow_anon: {
			type: 'bool',
			label: 'Anonymous Requests',
			edit: true
		},
		locked: {
			type: 'bool',
			edit: true
		},
		locked_by: {
			type: 'str',
			label: 'Locked By'
		}
	}));
});
