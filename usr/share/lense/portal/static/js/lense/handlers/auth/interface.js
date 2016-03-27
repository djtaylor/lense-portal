lense.import('Auth_Interface', function() {
	
	/**
	 * Initialize CSAuth
	 * @constructor
	 */
	this.__init__ = function() {
		(lense.url.param_exists('bootstrap')) ? lense.auth.bootstrap() : lense.auth.login(); 
	}
	
	/**
	 * Bootstrap Session
	 */
	this.bootstrap = function() {
		
		// Store session cookies
		$.each(['user', 'group', 'key', 'token', 'endpoint', 'session'], function(i,k) {
			Cookies.set(k, lense.url.param_get(k));
		});
		
		// Redirect to home
		lense.url.redirect('home');
	}
	
	/**
	 * Login User
	 */
	this.login = function() {
		
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
		
		// Look for authentication errors
		lense.auth.check_errors();
	}
	
	/**
	 * Check Authentication Errors
	 */
	this.check_errors = function() {
		if (lense.url.param_exists('error')) {
			auth_error = lense.url.param_get('error');
			
			// Show the authentication error
			$(".login_state").html(auth_error);
			lense.layout.fadein('.login_state');
			
			// Clean up the URL
			lense.url.param_del('error');
		}
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