lense.import('object.interface', function() {
	var self     = this;

	// Objects / grid containers
	this.objects = {};

	// Boolean flags to wait for data to load
	this.loaded  = {};

	// Access the current primary object
	this.primary = null;
	this.current = function() {
		return this.objects[self.primary];
	}

	/**
	 * Initialize Interface
	 * @constructor
	 */
	this.__init__ = function() {
		lense.implement([
		    'object.library'
		]);

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
	 * Wait for external data to load
	 */
	this.waitFor = function(key,submit) {
		self.loaded[key] = false;
		submit();
	}

	/**
	 * Blocking method to wait for all external calls to complete
	 */
	this.wait = function(callback) {
		var complete = true;
		$.each(self.loaded, function(k,v) {
			if (v === false) {
				complete = false;
			}
		});
		if (complete === true) {
			if (defined(callback)) {
				callback();
			}
		} else {
			setTimeout(self.wait, 100, callback);
		}
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
	 * Permissions interface
	 *
	 * @param {Object} data The permissions data
	 */
	function PermissionsInterface(data) {
		var local    = new BaseInterface('permissions', this);

		// Local data
		local.object = clone(data);

		/**
		 * Render a single permissions row
		 */
		local.render = function(permissions) {
			$('#object-permissions').append(Handlebars.helpers.object_permissions(permissions).string);
		}

		/**
		 * Construct permissions interface
		 */
		local.construct = function() {
			if ($.isArray(local.object)) {
				$.each(local.object, function(i,permissions) {
					local.render(permissions);
				});
			} else {
				local.render(local.object);
			}
		}

		return local;
	}

	/**
	 * Data interface
	 *
	 * @param {Object} data The data object
	 */
	function DataInterface(data,key) {
		console.log('Creating new data interface from: ' + data);
		var local    = new BaseInterface('data' + (defined(key) ? '.' + key:''), this);

		// Local data / additional data objects
		local.object  = clone(data);
		local.objects = {};

		/**
		 * Check if variable is inactive
		 *
		 * @param {Object} e The jQuery element selector
		 */
		local.isInactive = function(e) {
			return ((getattr(e, 'inactive', false) === false) ? false:true);
		}

		/**
		 * Store additional data interfaces
		 */
		local.define = function(k,d) {
			local.objects[k] = new DataInterface(d,k);
		}

		/**
		 * Access a specific data object by key
		 */
		local.as = function(k) {
			return local.objects[k];
		}

		/**
		 * Return the raw data value
		 */
		local.value = function() {
			return local.object;
		}

		/**
		 * Get variable type
		 *
		 * @param {Object} e The jQuery element selector
		 */
		local.getType = function(e) {
			var type = getattr(e, 'type');
			if ($.inArray(type, ['str', 'int', 'bool', 'array', 'object', 'meta']) == -1) {
				throw new Error('Invalid variable type: ' + type);
			}
			return type;
		}

		/**
		 * Get default value attribute
		 */
		local.getDefault = function(e) {
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
		local.getValue = function(e) {
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
		local.construct = function(parent, ref) {
			$.each(parent.children(), function(i,e) {
				var elem = $(e);
				if (elem.is('x-var')) {

					// Get variable attributes
					var type   = local.getType(elem);
					var def    = local.getDefault(elem);
					var active = (elem.is('[inactive]') ? false:true);
					var key    = (function() {
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

					// Is the element active or not
					if (!active) {
						return true;
					}

					// Variables with data-element attribute are no parse elements
					if (hasattr(elem, 'data-element')) {
						local.construct(elem, ref);

					// Other data types
					} else {

						// Parent data is array
						if ($.isArray(ref)) {
							if (key !== false) {
								throw new Error('Parent array cannot contain keyed element');
							}

							// Childless elements
							if ($.inArray(type, ['str', 'int', 'bool']) !== -1) {
								var value = local.getValue(elem);

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
								local.construct(elem, ref[ref.length - 1]);
							}

						// Assume object
						} else {
							if (key === false) {
								throw new Error('Parent object cannot contain un-keyed element')
							}

							// Key already defined
							if (hasattr(ref, key)) {
								throw new Error('Parent object contains duplicate key: ' + key);
							}

							// Childless elements
							if ($.inArray(type, ['str', 'int', 'bool']) !== -1) {
								var value = local.getValue(elem);

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
								local.construct(elem, ref[key]);
							}
						}
					}
				} else {
					local.construct(elem, ref);
				}
			});
		}

		/**
		 * Collect object data
		 *
		 * @param {String} id The ID of the parent variable object
		 */
		local.collect = function() {
			var top   = $('x-var[id="object-data"]');
			var type  = local.getType(top);
			var data  = (function() {
				switch(type) {
					case 'str':
					case 'bool':
					case 'int':
						return local.getValue(top);
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
				local.construct(top, data);
			} catch(e) {
				lense.log.warn(e);
				return undefined;
			}

			// Return data
			return data;
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
		}

		/**
		 * Iterate through data
		 *
		 * @param {Function} callback The iteration callback
		 */
		local.each = function(callback) {
			$.each(local.object, function(k,obj) {
				return callback(k,obj);
			});
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
		local.editor = ace.edit('object-source');

		// Theme / mode
		local.editor.setTheme(getattr(opts, 'theme', 'ace/theme/chrome'));
		local.editor.getSession().setMode(getattr(opts, 'mode', 'ace/mode/json'));

		// Autosize editor window
		local.editor.$blockScrolling = Infinity;
		local.editor.setOptions({
			maxLines: Infinity
		});

		// If data provided
		if (defined(data)) {
			local.editor.setValue(JSON.stringify(data, undefined, 2), -1);
		}

		// Read only (editing not supported)
		local.editor.setReadOnly(getattr(opts, 'readOnly', true));

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
	 * Grid objects interface. Use for managing multiple Gridstack objects
	 */
	function GridInterface() {
		var local = new BaseInterface('grid', this);

		// Available grid objects / current grid object
		local.grids = {};

		/**
		 * Define a new self-contained grid object
		 *
		 * @param {String} key The grid key
		 * @param {Object} opts Any additional options
		 */
		function GridObject(key, opts) {
			var local  = this;
			local.key  = key;
			local.opts = opts;
			local.id   = 'grid-' + key;
			local.data = getattr(opts, 'data', false);

			// Local grid object
			local.grid;

			/**
			 * Construct the current grid
			 */
			local.construct = function(data) {

				// Create the grid container
				$('#object-' + getattr(local.opts, 'pos')).html(
					'<x-var type="array" key="' + local.key + '" grid-key="' + local.key + '">' +
					'<div class="grid-stack" id="' + local.id + '"></div>' +
					'</x-var>'
				);

				// Setup Gridstack
				local.grid = $('#' + local.id);
				local.grid.gridstack({
					cellHeight: 40,
					verticalMargin: 10,
					draggable: {
						handle: '.object-move'
					}
				});

				// Set to static unless editing
				if (!lense.url.hasParam('edit')) {
					local.grid.data('gridstack').setStatic(true);
				}

				// Grid data should be defined
				if (!defined(data)) {
					lense.log.debug('Skipping grid "' + local.key + '" construction, data not defined...');
					return false;
				}

				// Data must be an array
				if ($.isArray(data)) {
					$.each(data, function(i,o) {
						$.each(o, function(item,attrs) {

							// Get grid type and key (optional)
							var item_type = (item.indexOf('#') >= 0) ? item.split('#')[0]:item;
							var item_key  = (item.indexOf('#') >= 0) ? item.split('#')[1]:null;

							// Create the grid object
							lense.object.library.mapType(item_type).create(local.grid, {
								key: item_key,
								data: attrs
							});
						});
					});
				} else {
					lense.log.warn('Grid data must be an array!');
				}
			}
		}

		/**
		 * Retrieve grid object by object ID
		 *
		 * @param {String} oid The grid object ID
		 */
		local.oid = function(oid) {
			var key = $('[object-id="' + oid + '"]').closest('x-var[grid-key]').attr('grid-key');
			return local.get(key);
		}

		/**
		 * Access grid as data key
		 *
		 * @param {String} key The grid key
		 */
		local.as = function(key) {
			if (!hasattr(local.grids, key)) {
				lense.raise('Cannot use "' + key + '" grid, not found!');
			}
			return local.grids[key];
		}

		/**
		 * Iterate through grids
		 *
		 * @param {Function} callback The loop callback
		 */
		local.each = function(callback) {
			$.each(local.grids, function(k, grid) {
				return callback(k, grid);
			});
		}

		/**
		 * Get grid object
		 *
		 * @param {String} key The grid key
		 */
		local.get = function(key) {
			if (!hasattr(local.grids, key)) {
				lense.raise('Cannot use "' + key + '" grid, not found!');
			}
			return local.grids[key].grid;
		}

		/**
		 * Define a new grid
		 *
		 * @param {String} key The grid key / data point
		 * @param {Object} opts Any additional options
		 */
		local.define = function(key, opts) {
			var id = 'grid-' + key;
			if (hasattr(local.grids, key)) {
				lense.raise('Cannot redefine grid: ' + key + '!');
			}
			local.grids[key] = new GridObject(key, opts);
		}

		/**
		 * Remove a grid object
		 *
		 * @param {String} oid The object ID
		 */
		local.remove = function(oid) {
			local.oid(oid).data('gridstack').removeWidget($('.grid-stack-item[object-id="' + oid + '"]'));
		}

		// Return the grid interface
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
		local.opts, local.template, local.source, local.data;
		local.properties = {};
		local.groups     = {};

		// Grid interface
		local.grid   = new GridInterface();

		// UUID and type
		local.uuid   = uuid;
		local.type   = type;

		// Create flag and checks
		local.create = (function() {
			var create = lense.url.getParam('create', false);
			if (create && local.uuid) {
				lense.raise('UUID and create parameters not compatible!');
			}
		}());

		// Edit flag and checks
		local.edit   = (function() {
			var edit = lense.url.getParam('edit', false);
			if (edit && local.create) {
				lense.raise('Create and edit parameters not compatible!');
			}
			if (edit && !defined(local.uuid)) {
				lense.raise('Cannot edit without selecting an object!');
			}
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
		 * Define an object grouping
		 *
		 * @param {String} pos The position to render
		 * @param {Object} filter The goups rendering properties
		 */
		local.defineGroup = function(pos, properties) {
			var members   = getattr(properties, 'members');
			var available = getattr(properties, 'available');
			var fields    = getattr(properties, 'fields');
			var title     = getattr(properties, 'title', 'Members');

			// If members object is an array, and you need to map values
			// to keys in available members as an object.
			var map       = getattr(properties, 'map', false);

			// Store rendering properties
			local.groups[pos] = {
				'members': members,
				'available': available,
				'title': title,
				'fields': fields,
				'map': map
			};
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
					if (include.contains(k)) {
						render.append(k,v);
					}
				});
			}

			// Excluding specific attributes
			if (exclude) {
				local.template.each(function(k,v) {
					if (!exclude.contains(k)) {
						render.append(k,v);
					}
				});
			}

			// Show all properties
			if (!include && !exclude) {
				render = local.template;
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
		local.defineGrid = function(pos, opts) {
			var key      = getattr(opts, 'key');
			var template = local.template.get(key);

			// Key must be in template
			if (!defined(template)) {
				lense.raise('Grid key "' + key + '" not found in object template!');
			}

			// Grid object types
			$.each(getattr(opts, 'require'), function(i,t) {
				getattr(lense.object.library, t).setup(key);
			});

			// Store the grid key
			local.grid.define(key, {
				pos: pos
			});
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
			$(document).on('click', 'button[btn-target]', function() {
				var elem    = $(this);
				var group   = getattr(elem, 'btn-group');
				var target  = getattr(elem, 'btn-target');

				// Ignore clicking the active button
				if (!elem.hasClass('active')) {

					// Switch button states
					$('button[btn-group="' + group + '"]').removeClass('active');
					$('button[btn-group="' + group + '"][btn-target="' + target + '"]').addClass('active');

					// Toggle content
					$('div[btn-group="' + group + '"]').css('display', 'none');
					$('div[btn-group="' + group + '"][btn-toggle="' + target + '"]').css('display', 'block');
				}
			});
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
			$.each(['input', 'blur', 'change', 'select', 'focus', 'focusout', 'focusin'], function(i,e) {
				$(document).on(e, '[update-source]', function() {
					var data = local.data.collect();
					if (!defined(data)) {
						lense.log.debug('Failed to update source: data undefined');
						return false;
					}
					local.source.update(data);
				});
			});

			// Edit object
			$(document).on('click', '#edit-object', function() {
				window.location.href = window.location.pathname + '?view=' + lense.url.getParam('view') + '&uuid=' + lense.url.getParam('uuid') + '&edit';
			});

			// Save object
			$(document).on('click', '#save-object', function() {
				console.log(local.data.collect());
			});

			// Cancel edit
			$(document).on('click', '#edit-object-cancel', function() {
				window.location.href = window.location.pathname + '?view=' + lense.url.getParam('view') + '&uuid=' + lense.url.getParam('uuid');
			});

			// Change list layout
			$(document).on('click', 'button[object-toggle-layout]', function() {
				self.setLayout(getattr($(this), 'object-toggle-layout'));
			});

			// Remove object
			$(document).on('click', '.object-remove', function() {
				local.grid.remove(getattr($(this), 'object-id'));
			});

			// Add data element
			$(document).on('click', 'button[data-add]', function() {
				var elem    = $(this);
				var oid     = getattr(elem, 'object-id');

				// Type of data to add
				var addType = getattr(elem, 'data-add');

				// Process based on data type to add
				switch(addType) {
					case "arg":
						var argType = getattr(elem, 'data-argtype');

						// Process based on argument type
						switch(argType) {
							case "arg":
							case "kwarg":
							default:
								lense.log.warn('Cannot add argument, invalid argument type: ' + argType)
						}
						break;

					// Invalid data point type
					default:
						lense.log.warn('Cannot add data point, invalid type: ' + addType);
				}
			});

			// Add argument
			$(document).on('click', 'button[object-arg-add]', function() {
				var elem = $(this);
				var oid  = getattr(elem, 'object-id');
				var type = getattr(elem, 'object-arg-add');
				var key  = getattr(elem, 'data-key');
				var html = null;

				// Process argument type
				switch(type) {
					case "arg":
					case "kwarg":
						html = $(Handlebars.helpers.object_arg(type, oid, { 'key': null, 'value': null, 'disabled': false}).string);
						break;
					case "param":
					  html = $(Handlebars.helpers.object_param(oid, '', [null, false]).string);
						break;
					default:
						lense.raise('Cannot add invalid argument type: ' + type);
				}

				// Target container
				$('x-var[object-id="' + oid + '"][key="' + key + '"]').append(html);

				// Resize widget
				local.resizeDetails(oid);
			});

			// Remove argument
			$(document).on('click', '.btn-remove-object-attr', function() {
				var uuid = getattr($(this), 'uuid');
				var oid  = getattr($(this), 'object-id');
				$('.object-attr-row[uuid="' + uuid + '"]').closest('x-var').remove();

				// Update source
				local.source.update(local.data.collect());
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

			// Add object widget
			$(document).on('click', 'button.btn-create-object', function() {
				var elem = $(this);
				var type = getattr(elem, 'object-type');
				var grid = getattr(elem, 'grid-key');

				// Ignore for keyed objects (create via modal)
				if (!hasattr(elem, 'object-keyed')) {
					lense.object.library.mapType(type).create(local.grid.get(grid), {
						disabled: false
					});
					lense.object.library.render({ disabled: false });
				} else {

					// Update modal hidden attributes
					$('#object-type').val(type);
					$('#object-grid').val(grid);
				}
			});

			// Add keyed object widget
			$(document).on('click', 'button#object-key-submit', function() {
				var type = $('#object-type').val();
				var grid = $('#object-grid').val();
				var key  = $('input[name="object-key"]').val();

				// Create the element
				try {
					lense.object.library.mapType(type).create(local.grid.get(grid), {
						key: key,
						disabled: false
					});
					lense.object.library.render({ disabled: false });

					// Hide the modal
					$('#object-key').modal('hide');

					// Reset the key input
					$('input[name="object-key"]').val('');

					// Reset modal hidden inputs
					$('#object-type').val('');
					$('#object-grid').val('');

				// Error creating object widget
				} catch (e) {
					lense.raise('Failed to create object: ' + e);
				}
			});

			// Data groups
			$(document).on('click', 'button[data-group]', function() {
				var group    = getattr($(this), 'data-group');
				var target   = getattr($(this), 'data-target');
				var oid      = getattr($(this), 'object-id');

				// All group objects
				var all      = {
					buttons: $('button[data-group="' + group + '"]'),
					children: $('div[data-parent="' + group + '"]'),
					xvar: $('x-var[data-parent="' + group + '"]')
				};

				// Selected objects
				var selected = {
					button: $('button[data-group="' + group + '"][data-target="' + target + '"]'),
					children: $('div[data-parent="' + group + '"][data-element="' + target + '"]'),
					xvar: $('x-var[data-parent="' + group + '"][data-element="' + target + '"]')
				};

				// Disable group
				if ($(this).hasClass('active')) {
					selected.button.removeClass('active');
					selected.children.css('display', 'none');
					selected.xvar.attr('inactive', '');

				// Switch groups
				} else {

					// Disable all buttons / children
					all.buttons.removeClass('active');
					all.children.css('display', 'none');
					all.xvar.attr('inactive', '');

					// Enable selected button / children
					selected.button.addClass('active');
					selected.children.css('display', 'block');
					selected.xvar.removeAttr('inactive');
				}

				// Resize widget
				local.resizeDetails(oid);

				// Update source
				if (hasattr($(this), 'update-source')) {
					local.source.update(local.data.collect());
				}
			});
		}

		/**
		 * Expand object details
		 *
		 * @param {String} id The object ID
		 */
		local.resizeDetails = function(oid) {
			var height = $('.object-collapse[object-id="' + oid + '"]').actual('height');
			var ysize  = Math.ceil(height / 40);

			// Resize the widget
			local.grid.oid(oid).data('gridstack').resize('.grid-stack-item[object-id="' + oid + '"]', null, (ysize == 1) ? 2: ysize);
		}

		/**
		 * Collapse object details
		 *
		 * @param {String} oid The object ID
		 */
		local.collapseDetails = function(oid) {
			local.grid.oid(oid).data('gridstack').resize('.grid-stack-item[object-id="' + oid + '"]', null, 1);
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
		 * Bootstrap group fields
		 *
		 * @param {Object} template The template to use for this position
		 */
		local.bootstrapGroups = function(attrs) {
			return Handlebars.helpers.object_group(attrs.title, {
				'members': local.data.get(attrs.members),
				'available': (function() {
					if (attrs.available.contains('.')) {
						return local.data.as(attrs.available.split('.')[1]).value();
					} else {
						return local.data.value();
					}
				})(),
				'fields': attrs.fields,
				'map': attrs.map
			}).string;
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
			return '<h4>' + local.type + (function() {
				if (defined(local.uuid)) {
					var title = local.uuid;
					local.template.each(function(k,obj) {
						if (hasattr(obj, 'link') && obj.link === true) {
							title = local.data.get(k);
						}
					});
					return '::' + title;
				} else if (local.create) {
					return '::create';
				} else {
					return 's';
				}
			}()) + '</h4>';

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
			$.each(local.data.object, function(i,object) {
				thumbnails.push(Handlebars.helpers.object_thumbnail(object, local.template));
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

			// Render rows
			$('#object-rows-body').html(rows.join(''));
			return '';
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
			function visible(loc) {
				return ($('#object-' + loc).css('display') == 'none') ? false:true;
			}

			// Size content columns
			function sizeColumns() {
				$('#object-' + pos).css('display', 'inline-block');
				var isVisible = [];
				$.each(['content-left', 'content-center', 'content-right'], function(i,current) {
					if (current != 'content-center') {
						visible(current) ? isVisible.push(current):null;
					}
				});

				// Resize center column
				$('#object-content-center').attr('class', ('col-md-' + (12 - (isVisible.length * 4)).toString()));
			}

			// Process location
			switch(pos) {
				case "content-left":
				case "content-center":
				case "content-right":
					sizeColumns(pos);
				case "header":
				case "list-controls":
				case "list-rows":
				case "list-thumbnails":
				case "footer":
				case "controls-create":
				case "sort":
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
					local.source = new SourceInterface(local.data.object);

					// Construct grids
					local.grid.each(function(key, grid) {
						local.render(grid.opts.pos)(grid.construct(local.data.get(key)));
					});

					// Construct properties
					$.each(local.properties, function(pos, attrs) {
						local.render(pos)(local.bootstrapProperties(attrs));
					});

					// Construct groups
					$.each(local.groups, function(pos, attrs) {
						local.render(pos)(local.bootstrapGroups(attrs));
					});

					break;
				default:
					lense.raise('Cannot construct interface, invalid view: ' + view);
			}

			// Post processing rendering
			lense.object.library.render();

			// Bind events
			local._bind();
		}

		/**
		 * Callback for object permissions
		 */
		lense.register.callback('permissionsResponse', function(data) {

			// New permissions object
			local.permissions = new PermissionsInterface(data);

			// Construct permissions
			local.permissions.construct();

			// Construct the view now for a single object
			local.construct();

			// If editing
			if (lense.url.hasParam('edit')) {
				local.editStart();
			}
		});

		/**
		 * Callback for supplementary data
		 */
		lense.register.callback('dataResponse', function(key,data) {
			local.data.define(key, data);
			self.loaded[key] = true;
		});

		 /**
		  * Callback for response data
			*/
    lense.register.callback('objectResponse', function(data) {

			// Setup the data interface
			local.data = new DataInterface(data);

			// Get permissions if viewing a single object
			if (defined(local.uuid)) {
					lense.api.request.submit('permissions_get', { 'object_uuid': local.uuid }, 'permissionsResponse');
			}

		  // Construct the view now if viewing a list of objects
			if (!defined(local.uuid)) {
				local.construct();
			}

			// Set the complete flag
			self.loaded['object'] = true;
		});

		 /**
 		 * Bootstrap the object
 		 */
 		local.bootstrap = function(options) {
			var data = getattr(options, 'data', false);

 			// Creating an object
 			if (local.create) {
 				return lense.callback['objectResponse'](local.template.object);
 			}

 			// Retrieve the primary object
			self.waitFor('object', function() {
				lense.api.request.submit(getattr(local.opts.handler, 'get'), (function() {
					if (defined(local.uuid)) {
						return {
			 				uuid: local.uuid,
			 			};
					}
					return null;
				}()), 'objectResponse');
			});

			// Wait to fetch the primary object
			self.wait(function() {

				// If retrieving secondary data
				if (data) {
					$.each(data, function(k,h) {
						self.waitFor(k, function() {
							lense.api.request.submit(h, null, 'dataResponse+' + k);
						});
					});

					// Wait for secondary data
					self.wait(function() {
						// Something to do after secondary data loaded
					});
				}
			});

			// Run the constructor
			local.construct();
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

		// Store the primary UUID
		self.primary = uuid;

		// Initialize the object
		if (hasattr(object, '__init__')) {
			object.__init__();
		}

		// Store / return the object
		self.objects[uuid] = object;
		return self.objects[uuid];
	}
});
