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

		// Object key modal shown
		$(document).on('shown.bs.modal', '#object-key', function() {
      $('input[name="object-key"]').focus();
    });

		// Object key modal hidden
		$(document).on('hidden.bs.modal', '#object-key', function() { });
	}

	/**
	 * Source Interface
	 */
	function SourceInterface(id, data, opts) {
		var inner = this;

		// Define the editor
		this.editor = ace.edit('object-source');

		// Theme / mode
		this.editor.setTheme(getattr(opts, 'theme', 'ace/theme/chrome'));
		this.editor.getSession().setMode(getattr(opts, 'mode', 'ace/mode/json'));

		// Read only
		this.editor.setReadOnly(getattr(opts, 'readOnly', true));

		// Autosize editor window
		this.editor.$blockScrolling = Infinity;
		this.editor.setOptions({
			maxLines: Infinity
		});

		// If data provided
		if (defined(data)) {
			this.editor.setValue(JSON.stringify(data, undefined, 2), -1);
		}

		// Return the source interface
		return this;
	}

	/**
	 * Object Interface
	 */
	function ObjectInterface(id, type, uuid) {
		var inner          = this;

		// Object ID / Type / UUID
		this.id            = id;
		this.type          = type;
		this.uuid          = (defined(uuid)) ? uuid:'create';

		// Widgets / grids
		this.widgets       = {};
		this.grids         = {};

		// Object source
		self.source        = null;

		/**
		 * @constructor
		 */
		this.__init__ = function() {

			// Toggle source
			$(document).on('click', '#view-object-source', function() {
				$('#view-object-source').css('display', 'none');
				$('#view-object-grid').css('display', 'inline-block');
				$('#object-content').css('display', 'none');
				$('#object-source').css('display', 'block');
			});

			// Toggle grid
			$(document).on('click', '#view-object-grid', function() {
				$('#view-object-grid').css('display', 'none');
				$('#view-object-source').css('display', 'inline-block');
				$('#object-source').css('display', 'none');
				$('#object-content').css('display', 'block');
			});
		}

		/**
		 * Set source data.
		 *
		 * @param {Object} data The object source data
		 */
		this.setData = function(data) {
			self.source = new SourceInterface(id, data);
		}

		/**
		 * Create a new grid object.
		 *
		 * @param {String} id The grid ID
		 * @param {String} type The grid object type
		 * @param {String} key The grid object key
		 * @param {Object} attrs The grid object attributes
		 */
		this.createGridObject = function(id, type, key, attrs) {
			try {
				lense.object.library.mapType(type).create(inner.grids[id], key, attrs);
			} catch (e) {
				lense.notify('warning', e);
			}
		}

		/**
		 * Convert source object to grid layout.
		 *
		 * @param {String} id The grid ID
		 * @param {Object} data Grid data objects
		 */
		this.sourceToGrid = function(id, data) {
			if ($.isArray(data)) {
				$.each(data, function(i,o) {
					$.each(o, function(item,attrs) {
						console.log('item=' + item + ', attrs=' + JSON.stringify(attrs));
						var type = (item.indexOf('#') >= 0) ? item.split('#')[0]:item;
						var key  = (item.indexOf('#') >= 0) ? item.split('#')[1]:null;
						inner.createGridObject(id, type, key, attrs);
					});
				});
			} else {
				lense.notify('warning', 'Grid data must be an array!');
			}
		}

		/**
		 * Render a grid editor.
		 *
		 * @param {String} loc The grid location
		 * @returns {Function}
		 */
		 this.renderGrid = function(loc) {
			 switch(loc) {
				 case "content-left":
				 case "content-right":
				 case "content-center":
				 	 return function(id, data, opts) {

						 // Create the grid container / source editor
						 $('#object-' + loc).html('<div class="grid-stack" object-grid="' + id + '"></div>');

						 // Define the grid
						 inner.grids[id] = $('div[object-grid="' + id + '"]');

						 // Setup the grid
						 inner.grids[id].gridstack({
							 cellHeight: 40,
									 verticalMargin: 10,
									 draggable: {
											 handle: '.object-move'
									 }
						 });

						 // Render data
						 if (defined(data)) {
							 var extract = getattr(opts, 'extract', false);

							 // Convert source to grid
							 inner.sourceToGrid(id, (extract !== false) ? data[extract]:data);
						 }

						 // Remove widget
			 			$(document).on('click', '.object-remove', function(i,e) {
							inner.grids[id].data('gridstack').removeWidget('div[object-id="' + getattr($(this), 'object-id') + '"]');
			 			});
					 }
				 	 break;
				 default:
					 lense.notify('warning', 'Invalid layout location: ' + loc);
			 }
		 }

		/**
		 * Render an object pane.
		 *
		 * @param {String} loc The pane location
		 * @returns {Function}
		 */
		 this.render = function(loc) {

			 /**
			  * Is location visible
				*
				* @param {String} loc The location to check
				*/
			 function visible(loc) {
				 return ($('#object-' + loc).css('display') == 'none') ? false:true;
			 }

			 /**
			  * Render worker
				*
				* @param {String} loc The position location
				*/
			 function worker(loc) {

				 /**
				  * Inner method
					*
					* @param {Object} html The HTML object to append
					* @param {Boolean} flush Clear out previous content or not
					*/
				 return function(html, flush) {
					 if (flush === true) {
						 $('#object-' + loc).html(html);
					 } else {
						 $('#object-' + loc).append(html);
					 }
				 }
			 }

			 /**
			  * Size content columns
				*
				* @param {String} loc The location being targeted
				*/
			 function sizeColumns(loc) {
				 var isVisible = [];
				 $.each(['content-left', 'content-center', 'content-right'], function(i,current) {
					 if (current != 'content-center') {
						 visible(current) ? isVisible.push(current):null;
					 }
				 });

				 // Calculcate center column size
				 var centerSize = (12 - (isVisible.length * 3));

				 // Resize center column
				 $('#object-content-center').attr('class', 'col-md-' + centerSize.toString());
			 }

			 try {

				 // Process location
				 switch(loc) {
					 case "header":
					 	$('#object-header').html('<h4>' + this.type + '::' + this.uuid + '</h4>');
						break;
					 case "content-left":
					 case "content-center":
					 case "content-right":
					  $('#object-' + loc).css('display', 'inline-block');
					  sizeColumns(loc);
					 	return worker(loc)
					 case "footer":
	 				 case "source":
	 				 case "controls-create":
					 	return worker(loc)
						break;
					 default:
					 	return function() {
							lense.notify('warning', 'Invalid layout location: ' + loc);
						}
					}

			 } catch(e) {
				 lense.notify('warning', e);
			 }
		 }

		/**
		 * Load required object types
		 *
		 * @param {Array} types An array of registered object types
		 */
		this.require = function(types) {
			$.each(types, function(i,t) {

				// Get the object type definition
				var type = getattr(lense.object.library, t);

				// Setup the object type
				type.setup();
			});
		}

		/**
		 * Define a properties panel.
		 *
		 * @param {Object} data Handler details
		 * @param {Object} opts Any additional options
		 */
		 this.defineProperties = function(data, opts) {
			 return 'Stuff';
		 }
	}

	/**
	 * Define a new object interface
	 *
	 * @param {String} type The object type
	 * @param {String} [uuid] The object UUID if loading an existing object
	 * @returns {ObjectInterface}
	 */
	this.define = function(type, uuid) {
		var inner = (defined(uuid)) ? uuid:'create';
		self.objects[inner] = new ObjectInterface(inner, type, uuid);
		self.objects[inner].__init__();
		return self.objects[inner];
	}
});
