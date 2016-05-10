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
			
			// Fade in the login window
			$('.form-login-container').animate({
				opacity: 1.0
			}, 1000);
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
			$("#form-login-error").html(auth_error);
			lense.common.layout.fadein('#form-login-error');
			
			// Clean up the URL
			lense.common.url.param_del('error');
		}
	}
	
	/**
	 * Bind Login Form
	 */
	this._bind = function() {
		
		// Click login button
		$(document).on('click', '#form-login-button', function() {
			$('#form-login').submit();
		});
		
		// Press enter in login form
		$(document).on('keypress', function(e) {
			if (e.which == 13) {
		        e.preventDefault();
		        $("#form-login").submit();
		    }
		});
	}
});