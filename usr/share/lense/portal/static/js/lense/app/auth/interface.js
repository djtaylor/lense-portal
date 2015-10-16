/**
 * Lense Authentication
 */
lense.import('LenseAuthInterface', function() {
	
	/**
	 * Initialize CSAuth
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Bind click/enter
		lense.auth.bind();
		
		// Document ready
		$(document).ready(function() {
			lense.auth.layout();
			
			// Fade in the login window
			$('.login_window').animate({
				opacity: 1.0
			}, 1000);
		});
		
		// Window resize
		$(window).resize(function() {
			lense.auth.layout();
		});
	}
	
	/**
	 * Set Layout
	 */
	this.layout = function() {
		
		// Login window attributes
		var login = {
			width:  $('.login_window').actual('outerWidth', {includeMargin: true}),
			height: $('.login_window').actual('outerHeight', {includeMargin: true})
		}
		
		// Parent page attributes
		var page = {
			width:  $(window).width(),
			height: $(window).height()
		}
		
		// Set the login window position
		$('.login_window').css('left', ((page.width / 2) - (login.width / 2)) + 'px');
		$('.login_window').css('top', ((page.height / 2) - (login.height)) + 'px');
	}
	
	/**
	 * Bind Login Form
	 */
	this.bind = function() {
		
		// Click login button
		$(document).on('click', '.login_submit', function() {
			$('#login_form').submit();
		});
		
		// Press enter in login form
		$(document).on('keypress', function(e) {
			if (e.which == 13) {
		        e.preventDefault();
		        $("#login_form").submit();
		    }
		});
	}
});