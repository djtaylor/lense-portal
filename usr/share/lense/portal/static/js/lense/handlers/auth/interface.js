lense.import('auth.interface', function() {
	
	/**
	 * Initialize CSAuth
	 * @constructor
	 */
	this.__init__ = function() {
		(lense.common.url.param_exists('bootstrap')) ? lense.auth._bootstrap() : lense.auth._login(); 
	}
	
	/**
	 * Bootstrap Session
	 */
	this._bootstrap = function() {
		
		// Store session cookies
		$.each(['user', 'group', 'key', 'token', 'endpoint', 'session'], function(i,k) {
			Cookies.set(k, lense.common.url.param_get(k));
		});
		
		// Redirect to home
		lense.common.url.redirect('home');
	}
	
	/**
	 * Login User
	 */
	this._login = function() {
		
		// Bind click/enter
		lense.auth._bind();
		
		// Document ready
		$(document).ready(function() {
			lense.auth._layout();
			
			// Fade in the login window
			$('.login_window').animate({
				opacity: 1.0
			}, 1000);
		});
		
		// Window resize
		$(window).resize(function() {
			lense.auth._layout();
		});
		
		// Look for authentication errors
		lense.auth._check_errors();
	}
	
	/**
	 * Check Authentication Errors
	 */
	this._check_errors = function() {
		if (lense.common.url.param_exists('error')) {
			auth_error = lense.common.url.param_get('error');
			
			// Show the authentication error
			$(".login_state").html(auth_error);
			lense.common.layout.fadein('.login_state');
			
			// Clean up the URL
			lense.common.url.param_del('error');
		}
	}
	
	/**
	 * Set Layout
	 */
	this._layout = function() {
		
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
	this._bind = function() {
		
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