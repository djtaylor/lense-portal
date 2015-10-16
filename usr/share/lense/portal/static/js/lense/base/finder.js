lense.import('LenseBaseFinder', function() { 
	
	// Key codes
	this.keycode = {
		down:  40,
		up:    38,
		enter: 13
	}
	
	// Results index
	this.index = {
		focus: 1
	}
	
	// Search shortcuts
	this.shortcuts = {
		home:        '/home',
		users:       '/admin?panel=users',
		groups:      '/admin?panel=groups',
		acls:        '/admin?panel=acls',
		utilities:   '/admin?panel=utilities',
		objects:     '/admin?panel=objects'
	}
	
	// Object type labels
	this.otype_labels = {
		user:       'API Users',
		group:      'API Groups',
		utility:    'Utilities'
	};
	
	/**
	 * Initialize LenseBaseFinder
	 * @constructor
	 */
	this.__init__ = function() {
		lense.finder.bind();
	}
	
	/**
	 * Callback: Finder Results
	 */
	lense.register.callback('finder.results', function(c,m,d,a) {
		if (c == 200) {
			
			// Remove old results
			$('.finder_content').html('');
			
			// Reset the focus index
			lense.finder.index.focus = 1;
			
			// If any results returned
			if (m instanceof Array && m.length > 0) {
			
				// Break the results into object types
				var r = {};
				$.each(m, function(i,o) {
					if (!r.hasOwnProperty(o.type)) {
						r[o.type] = [];
					}
					r[o.type].push(o);
				});
				
				// Construct each object type group
				var _i = 1;
				$.each(r, function(t,o) {
					$('.finder_content').append(lense.layout.create.element('div', {
						css: 'finder_result_group',
						children: [
						    lense.layout.create.element('div', {
						    	css: 'finder_result_type',
						    	text: lense.finder.otype_labels[t]
						    }),
						    lense.layout.create.element('div', {
						    	css: 'finder_result_rows',
						    	children: (function() {
						    		var c = [];
						    		$.each(o, function(i,_o) {
						    			c.push(lense.layout.create.element('div', {
											css: 'finder_result_row',
											attr: {
												index: _i,
												link:  _o.url
											},
											text: _o.label
										}));
						    			_i++;
						    		});
						    		return c;
						    	})()
						    })
						]
					}));
				});
				
				// Make sure the finder results are visible
				if ($('#finder_results').css('display') != 'block') {
					$('#finder_results').fadeIn('fast');
				}
			} else {
				$('#finder_results').css('display', 'none');
			}
		}
	});
	
	/**
	 * Search Index
	 */
	this.search = function(t) {
		lense.api.request.get({
			path: 'cluster',
			action: 'search',
			_data: {
				string: t
			},
			callback: {
				id: 'finder.results'
			}
		});
	}
	
	/**
	 * Bind Events
	 */
	this.bind = function() {
		
		// Detect click on result row
		$(document).on('click', '.finder_result_row', function(e) {
			window.location = get_attr(this).link;
		});
		
		// Detect finder shortcut
		$(document).on('keyup', function(e) {
			if (e.shiftKey && (e.which == 70)) {
				$('#finder').focus();
			}
		});
		
		// Focus on finder input
		$(document).on('focus', '#finder', function(e) {
			$('#finder').val('');
		});
		
		// Blur finder input focus
		$(document).on('blur', '#finder', function(e) {
			$('#finder_results').fadeOut('fast', function() {
				$('#finder').val('Shift+F to search...');
			});
			
			// Remove any focused results
			$('.finder_result_row').removeAttr('focus');
			
			// Reset the focus index
			lense.finder.index.focus = 1;
		});
		
		// Toggle through finder results
		$('#finder').keyup(function(e) {
			
			// Get the text value
			var v = $('#finder').val();
			
			// Look for finder shortcuts
			if (e.keyCode == lense.finder.keycode.enter && v in lense.finder.shortcuts) {
				window.location = lense.finder.shortcuts[v];
			}
			
			// Only handle keypresses if results are shown
			if ($('#finder_results').css('display') == 'block') {
				
				// Get all finder result rows
				var r = $('.finder_result_row');
				
				// Get the total number of result rows
				var t = r.length;
				
				// Look for an focused result
				var f = $('.finder_result_row[focus]');
				
				// Enter
				if (e.keyCode == lense.finder.keycode.enter) {
					
					// Load the focused result
					if (f.length > 0) {
						$('.finder_result_row[index="' + lense.finder.index.focus + '"]').animate({
							opacity: 0.5
						}, 30).animate({
							opacity: 1.0
						}, 30);
						
						// Go to the result URL
						window.location = f.attr('link');
					}
				}
				
				// Down
				if (e.keyCode == lense.finder.keycode.down) {
					if (f.length > 0) {
						lense.finder.index.focus = ((lense.finder.index.focus + 1) > t) ? 1 : lense.finder.index.focus + 1;
					}
					$('.finder_result_row').removeAttr('focus');
					$('.finder_result_row[index="' + lense.finder.index.focus + '"]').attr('focus', '');
				}
				
				// Up
				if (e.keyCode == lense.finder.keycode.up) {
					if (f.length > 0) {
						lense.finder.index.focus = ((lense.finder.index.focus - 1) < 1) ? t : lense.finder.index.focus - 1;
					}
					$('.finder_result_row').removeAttr('focus');
					$('.finder_result_row[index="' + lense.finder.index.focus + '"]').attr('focus', '');
				}
			}
		});
		
		// Finder input detection
		$(document).on('input', '#finder', function(e) {
			
			// Get the finder text value
			var t = $(this).val();
			
			// If the text value is not empty
			if (defined(t)) {
				lense.finder.search(t);
			}
		});
	}
});