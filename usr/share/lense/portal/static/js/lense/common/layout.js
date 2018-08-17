lense.import('common.layout', function() {
	var self = this;
	
	/**
	 * Notifications
	 * 
	 * @param {type}    The notification type
	 * @param {message} The message to display
	 */
	this.notify = function(type, message) {
		$.notify({
			message: message, 
		},{
			type: type,
			placement: {
				from: "bottom",
				align: "right"
			},
			delay: 2000
		});
	}
	
	/**
	 * Swap Element Visibility
	 * 
	 * Wrapper method for toggling visibility between two elements.
	 */
	this.swap = function(a,b) {
		var a_vis = $(a).css('display');
		var b_vis = $(b).css('display');
		
		// A = hidden
		if (a_vis == 'none') {
			$(b).css('display', 'none');
			$(a).css('display', 'block');
		}
		
		// B = hidden
		if (b_vis == 'none') {
			$(a).css('display', 'none');
			$(b).css('display', 'block');
		}
	}
	
	/**
	 * Fade Out Element
	 * 
	 * Wrapper method to fade out an element because. No real point in this method,
	 * but since I have 'fadein' might as well have 'fadeout'.
	 * 
	 * @param {f} A jQuery selector
	 * @param {c} A callback function
	 */
	this.fadeout = function(f,c) {
		$(f).fadeOut('fast', function() {
			if (defined(c)) {
				c();
			}
		});
	}
	
	/**
	 * Fade In Element
	 * 
	 * Wrapper method to fade in an element that is either set to hidden or opacity
	 * is set to 0.
	 * 
	 * @param {f} A jQuery selector
	 * @param {c} A callback function
	 */
	this.fadein = function(f,c) {
		if ($(f).css('display') == 'none') {
			$(f).fadeIn('fast');
		}
		if ($(f).css('opacity') == 0) {
			$(f).animate({
				opacity: 1.0
			}, 100);
		}
		if (defined(c)) {
			c();
		}
	}
	
	/**
	 * Remove Element
	 * 
	 * Fade out then completely remove an element from the DOM.
	 * 
	 * @param {f} A jQuery selector
	 */
	this.remove = function(f) {
		$(f).fadeOut('fast', function() {
			this.remove();
		});
	}
	
	/**
	 * Get HTML
	 * 
	 * Helper method to flatten either a single or array of jQuery nodes into a single
	 * HTML string.
	 * 
	 * @param {e} Either a single jQuery node or an array of nodes
	 */
	this.html = function(e) {
		if (e instanceof jQuery) {
			return e[0].outerHTML;
		} else {
			ha = [];
			$.each(e, function(i,o) {
				ha.push(o[0].outerHTML);
			});
			return ha.join('');
		}
	}
	
	/**
	 * Layout Completed
	 */
	this.complete = function() {
		var t = ['.table_headers', '.table_row'];
		$.each(t, function(i,k) {
			$.each($(document).find(k), function(i,o) {
				$(this).delay(20*i).animate({
					opacity: 1.0
				}, 100);
			});
		});
	}
	
	/**
	 * Refresh Page Layout
	 * 
	 * Wrapper method used to refresh various elements on the page, after setting new
	 * content, updating tables, etc.
	 * 
	 * @param {p} Optional parameters that can be passed to the internal methods
	 */
	this.refresh = function(p) {
		
		// Set up the page
		$.each(lense.common.layout.set, function(f,o) {
			if (f !== 'popups') {
				lense.common.layout.set[f]();
			}
		});
		
		// Resizable elements
		$('div[resizable]').resizable({
			minHeight: 500,
			minWidth:  500,
			create: function(e,u) {
				lense.common.layout.set.popups(e.target);
			},
			resize: function(e,u) {
				lense.common.layout.set.popups(e.target);
			}
		});
		
		// If centering any elements
		if (defined(p) && p.hasOwnProperty('center')) {
			lense.common.layout.center_elem(p.center);
		}
		
		// Layout ready
		lense.common.layout.complete();
	}
});