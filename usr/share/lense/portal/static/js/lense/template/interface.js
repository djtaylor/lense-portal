lense.import('template.interface', function() {
	var self = this;

	/**
	 * Div helper
	 *
	 * @param {Object} attrs Div attributes
	 * @param {Object} inner Any inner content
	 * @param {String} type The element type
	 */
	function div(attrs, inner, type) {
		var type  = ((defined(type)) ? type:'div');
		var attrs = (function() {
			var attrs_str = '';
			$.each(attrs, function(k,v) {
				attrs_str += ' ' + ((v === true) ? k:k + '="' + v + '"');
			});
			return attrs_str;
		}());

		// Return the div
		return '<' + type + attrs + '>' + ((defined(inner)) ? (function() {
			return inner();
		}()):'') + '</' + type + '>';
	}

	// Element wrappers
	function tr(attrs, inner) { return div(attrs, inner, 'tr'); }
	function th(attrs, inner) { return div(attrs, inner, 'th'); }
	function span(attrs, inner) { return div(attrs, inner, 'span'); }

	/**
	 * Initialize Interface
	 * @constructor
	 */
	this.__init__ = function() {

		// Null helper
		Handlebars.registerHelper('null', function() {
			return null;
		});

		// Undefined helper
		Handlebars.registerHelper('undefined', function() {
			return undefined;
		});

		// True helper
		Handlebars.registerHelper('true', function() {
			return true;
		});

		// False helper
		Handlebars.registerHelper('false', function() {
			return false;
		});
	}

	/**
	 * Compile a Handlebars template.
   *
   * @param {String} id The template ID
   * @param {Object} data Any template data
	 * @param {Object} opts Any additional options
	 */
	this.compile = function(id, data, opts) {
		var compiler = {};
		compiler.compiled = Handlebars.compile($('#' + id).html())(data);

		/**
		 * Return compiled HTML
		 */
		compiler.html = function() {
			return compiler.compiled
		}

		// Return the compiler object
		return compiler
	}

	/**
	 * Create select option
	 *
	 * @param {String} value The option value attribute
	 * @param {Object} opts Any additional options
	 */
	this.html = {
		selectOption: function(value, opts) {
			var label = getattr(opts, 'label', value);
			var state = ((getattr(opts, 'current', '') === value) ? ' selected="selected"':'');
			return '<option value="' + value + '"' + state + '>' + label + '</option>';
		},
		button: function(label, opts) {
			var type  = getattr(opts, 'type', 'default');
			var attrs = (function() {
				var attrs_str = '';
				$.each(getattr(opts, 'attrs', {}), function(k,v) {
					attrs_str += ' ' + ((v === true) ? k:k + '="' + v + '"');
				});
				return attrs_str;
			}());
			var modal = (function() {
				var modal_target = getattr(opts, 'modal', false);
				if (modal_target) {
					return ' data-toggle="modal" data-target="#' + modal_target + '"';
				}
				return '';
			}());
			return '<button type="button" class="btn btn-' + type + '"' + modal + attrs + '>' + label + '</button>';
		},
		buttonLink: function(label, opts) {
			var type   = getattr(opts, 'type', 'default');
			var url    = getattr(opts, 'url', window.location.pathname);
			var params = (function() {
				var params_inner = getattr(opts, 'params', null);
				if (defined(params_inner)) {
					return '?' + (function() {
						var params_array = [];
						$.each(params_inner, function(k,v) {
							params_array.push(k + ((v === true) ? '':'=' + v));
						});
						return params_array.join('&');
					}());
				} else {
					return '';
				}
			}());
			return '<a class="btn btn-' + type + '" href="' + url + params + '">' + label + '</a>';
		},
		objectHeaders: function(template) {
			return tr({}, function() {
				var headers = [th({ class: 'table-checkbox-col'})];
				template.each(function(key,attrs) {
					if (attrs.list) {
						headers.push(th({} , function() {
							return getattr(attrs, 'label', key);
						}));
					}
				});
				return headers.join('');
			});
		},
		objectRow: function(object, opts) {
			var template   = getattr(opts, 'template');
			var title_link = getattr(opts, 'title_link');

			// Parent block
			return tr({ uuid: object.uuid }, function() {
				var columns = [th({ scope: 'row', type: 'checkbox', uuid: object.uuid }, function() {
					return '<input type="checkbox" value="' + object.uuid + '" uuid>';
				})];

				// Construct columns
				template.each(function(k, attrs) {
					if (attrs.list) {
						columns.push((function() {
							if (getattr(attrs, 'link', false)) {
								return th({}, function() { return '<a href="' + title_link + '">' + object[key] + '</a>'; });
							} else {
								return th({}, function() { return (function() {
									var map = getattr(attrs, 'map', false);
									if (map) {
										var retval = null;
										$.each(map, function(label, value) {
											if (value === object[key]) {
												retval = label;
											}
										});
										return retval;
									} else {
										return (($.inArray(object[key], [null, undefined, '']) > -1) ? '':object[key]);
									}
								}()); });
							}
						}()));
					}
				});
				return columns.join('');
			});
		},
		kwargField: function(oid, key, value) {
			var uuid = {
				'element': lense.uuid4(),
				'key': lense.uuid4(),
				'value': lense.uuid4()
			};

			// Parent div
			return div({ 'class': 'row object-attr-row', 'object-id': oid, 'uuid': uuid.element }, function() {
				var objects = [];

				// Kwarg key field
				objects.push(div({ 'class': 'col-xs-2 col-object-attr-left col-object' }, function() {
					return '<input type="text" class="form-control object-input object-kwarg-input" placeholder="key" value="' + key + '" uuid="' + uuid.key + '" update-source disabled edit>';
				}));

				// Kwarg value field
				objects.push(div({ 'class': 'col-xs-9 col-object-center col-object' }, function() {
					return '<input type="text" class="form-control object-input" placeholder="value" value="' + value + '" uuid="' + uuid.value + '" update-source disabled edit>';
				}));

				// Remove kwarg button
				objects.push(div({ 'class': 'col-xs-1 col-object-attr-right col-object' }, function() {
					return '<button type="button" class="btn btn-danger btn-remove-object-attr" object-id="' + oid + '" uuid="' + uuid.element + '" update-source disabled edit>' +
					'<span class="glyphicon glyphicon-remove"></span>' +
					'</button>';
				}));

				// Xvar object
				objects.push('<x-var type="str" key="@input[uuid=\'' + uuid.key + '\']" value="input[uuid=\'' + uuid.value + '\']"></x-var>');

				// Return kwarg field
				return objects.join('');
			});
		},
		objectThumbnail: function(object, opts) {
			var template   = getattr(opts, 'template');
			var title_link = getattr(opts, 'title_link');
			var title_name = getattr(opts, 'title_name');

			// Parent block
			return div({ class: 'col-md-3 col-sm-4 col-xs-6', uuid: object.uuid }, function() {
				return div({ class: 'thumbnail object-thumbnail' }, function() {
					var thumbnailContent = [];

					// Generate thumbnail header
					thumbnailContent.push(div({ class: 'thumbnail-header' }, function() {
						var headerContent = [];
						headerContent.push('<div class="thumbnail-icon"><span class="glyphicon glyphicon-info-sign"></span></div>');
						headerContent.push('<div class="thumbnail-title"><a href="' + title_link + '">' + title_name + '</a></div>');
						headerContent.push('<div class="thumbnail-selector"><input type="checkbox" value="' + object.uuid + '" uuid></div>');
						return headerContent.join('');
					}));

					// Generate property fields
					template.each(function(key, attrs) {
						thumbnailContent.push(div({ class: 'input-group thumbnail-field' }, function() {
							var fieldContent = [];
							var fieldLabel   = getattr(attrs, 'label', key);
							var fieldValue   = (function() {
								var map = getattr(attrs, 'map', false);
								if (map) {
									var retval = null;
									$.each(map, function(label, value) {
										if (value === object[key]) {
											retval = label;
										}
									});
									return retval;
								} else {
									return (($.inArray(object[key], [null, undefined, '']) > -1) ? '':object[key]);
								}
							}());
							fieldContent.push('<span class="input-group-addon thumbnail-field-label">' + fieldLabel + '</span>');
							fieldContent.push('<input type="text" class="thumbnail-field-value form-control" value="' + fieldValue + '" readonly>');
							return fieldContent.join('');
						}));
					});

					// Return the contents
					return thumbnailContent.join('');
				});
			});
		}
	}
});
