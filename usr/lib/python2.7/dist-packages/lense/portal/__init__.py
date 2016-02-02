__version__ = '0.1'

class PortalTemplate(object):
    """
    Class for handling Django template attributes and functionality.
    """
    def __init__(self):
        self.data = None
        
    def construct(self, data):
        """
        Construct portal template attributes.
        """
        self.data = data

    def response(self):
        """
        Construct and return the template response.
        """
        
        # If redirecting
        if 'redirect' in self.data:
            return LENSE.HTTP.redirect(self.data['redirect'])
        
        # Return the template response
        try:
            return render(LENSE.REQUEST.DJANGO, 'interface.html', self.data)
        
        # Failed to render template
        except Exception as e:
            LENSE.LOG.exception('Internal server error: {0}'.format(str(e)))
            
            # Get the exception data
            e_type, e_info, e_trace = sys.exc_info()
            e_msg = '{0}: {1}'.format(e_type.__name__, e_info)
            
            # Return a server error
            return LENSE.HTTP.browser_error('core/error/500.html', {
                'error': 'An error occurred when rendering the requested page',
                'debug': None if not LENSE.CONF.portal.debug else (e_msg, reversed(traceback.extract_tb(e_trace)))
            })

class PortalInterface(object):
    """
    Interface class for portal commons.
    """
    def __init__(self):
        
        # Load handlers / controllers
        self.handlers    = LENSE.MODULE.handlers(ext='views', load='HandlerView')
        self.controllers = LENSE.MODULE.handlers(ext='controller', load='HandlerController')
        
        # Template container
        self.TEMPLATE    = PortalTemplate()
        
        # Bootstrap the portal interface
        self._set_session()
        
    def _set_session(self):
        """
        Set session variables.
        """
        if LENSE.REQUEST.USER.authorized:
            
            # Get the user details
            user   = LENSE.OBJECTS.USER.get(LENSE.REQUEST.USER.name)
            groups = user.groups
            
            # Set the 'is_admin' flag
            LENSE.REQUEST.SESSION.set('is_admin', user.is_admin)
            
            # If the active group hasn't been set yet
            if not LENSE.REQUEST.SESSION.get('active_group'):
                LENSE.REQUEST.SESSION.set('active_group', groups[0]['uuid'])
                
    def set_active_group(self, group):
        """
        Change the session variable for the active API user group.
        """
        user = LENSE.OBJECTS.USER.get(username=LENSE.REQUEST.USER.name)
        
        # Make sure the user is a member of the group
        is_member = False
        for usr_group in user.groups:
            if usr_group['uuid'] == group:
                is_member = True
                break 
        
        # If the group is valid
        if is_member:
            LENSE.REQUEST.SESSION.set('active_group', group)