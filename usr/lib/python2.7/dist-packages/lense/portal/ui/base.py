from django.contrib.auth import logout

class PortalBase(object):
    """
    Base class shared by all Lense portal views. This is used to initialize
    requests, construct template data, set the logger, etc.
    """
    def __init__(self):
        

        # Bootstrap the session
        self._set_session()
        
        # If the user is authenticated
        if LENSE.REQUEST.user.authorized:
            
            # Initialize the API client
            LENSE.SETUP.client(
                user  = LENSE.REQUEST.USER.name,
                group = LENSE.REQUEST.USER.group,
                key   = LENSE.OBJECTS.USER.get_key(LENSE.REQUEST.USER.name)
            )
            
            # Get an API token
            LENSE.CLIENT.authorize()
        
        # Construct and return the application template
        self.template = self._run_controller()

    
        
    def _run_controller(self, **kwargs):
        """
        Run the target application controller.
        """
        
        # If the user is authenticated
        if LENSE.REQUEST.user.authorized:
            
            # Redirect to home page if trying to access the login screen
            if LENSE.REQUEST.path == 'auth':
                return LENSE.HTTP.redirect('home')
            
            # Return the template response
            return self.controller[LENSE.REQUEST.path](self).construct(**kwargs)
            
        # User is not authenticated
        else:
            
            # Redirect to the login screen if trying to access any other page
            if not LENSE.REQUEST.path == 'auth':
                return LENSE.HTTP.REDIRECT('auth')
            
            # Return the template response
            return self.controller[LENSE.REQUEST.path]().construct(**kwargs)
        
    
        
    def login(self, username, password):
        """
        Login a user account.
        """
        
        # User exists and is authenticated
        if LENSE.USER.AUTHENTICATE(user=username, password=password):
            
            # User is active
            if LENSE.REQUEST.user.active:
                LENSE.LOG.info('User account [{0}] active, logging in user'.format(username))
                
                # Login the user account
                LENSE.USER.LOGIN(LENSE.REQUEST.DJANGO, username)
                
                # Redirect to the home page
                return LENSE.HTTP.redirect('/home')
            
            # User account is inactive
            else:
                LENSE.LOG.info('Login failed, user account "{0}" is inactive'.format(username))
                state = 'Your account is disabled - please contact your administrator'
        
        # User account does not exist or username/password incorrect
        else:
            LENSE.LOG.error('Login failed, user account "{0}" does not exist or password is incorrect'.format(username))
            state = 'Your username and/or password are incorrect'
    
        # Return the login failure screen
        return self._run_controller(state=state, state_display='block')
        
    def logout(self):
        """
        Logout the current user.
        """
        logout(self.request.RAW)
        
        # Return the base object
        return self