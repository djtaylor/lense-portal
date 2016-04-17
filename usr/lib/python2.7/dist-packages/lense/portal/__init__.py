__version__ = '0.1'

# Lense Libraries
from lense.common.exceptions import RequestError

class PortalBase(object):
    def log(self, msg, level='info', method=None):
        """
        Wrapper method for logging with a prefix.
        
        :param    msg: The message to log
        :type     msg: str
        :param  level: The desired log level
        :type   level: str
        :param method: Optionally append the method to log prefix
        :type  method: str
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<TEMPLATE:{0}{1}:{2}@{3}> {4}'.format(
            self.__class__.__name__, 
            '' if not method else '.{0}'.format(method), 
            LENSE.REQUEST.USER.name,
            LENSE.REQUEST.client,
            msg
        ))

class PortalInterface(PortalBase):
    """
    Interface class for portal commons.
    """
    def __init__(self):
        
        # Load handlers / controllers
        self.handlers    = LENSE.MODULE.handlers(ext='views', load='HandlerView')
        self.controllers = LENSE.MODULE.handlers(ext='controller', load='HandlerController')
        
        # Template / assets handler
        self.TEMPLATE    = LENSE.import_class('PortalTemplate', 'lense.portal.ui.core.template')
        self.ASSETS      = LENSE.import_class('PortalAssets', 'lense.portal.ui.core.assets')
        
        # Bootstrap the portal interface
        self._set_session()
        
    def controller(self, **kwargs):
        """
        Run the target application controller.
        """
        
        # If the user is authenticated
        if LENSE.REQUEST.USER.authorized:
            
            # Redirect to home page
            if (LENSE.REQUEST.path == 'auth') and not (LENSE.REQUEST.data.get('bootstrap')):
                return LENSE.HTTP.redirect('home')
            
            # Return the template response
            return self.controllers[LENSE.REQUEST.path]().construct(**kwargs)
            
        # User is not authenticated
        else:
            
            # Redirect to the login screen if trying to access any other page
            if not LENSE.REQUEST.path == 'auth':
                return LENSE.HTTP.redirect('auth')
            
            # Return the template response
            return self.controllers[LENSE.REQUEST.path]().construct(**kwargs)
        
    def _set_session(self):
        """
        Set session variables.
        """
        if LENSE.REQUEST.USER.authorized:
            
            # Get the user details
            user   = LENSE.OBJECTS.USER.get(username=LENSE.REQUEST.USER.name)
            groups = user.groups
            
            # Set the 'is_admin' flag
            LENSE.REQUEST.SESSION.set('is_admin', LENSE.REQUEST.USER.admin)
            
            # If the active group hasn't been set yet
            if not LENSE.REQUEST.SESSION.get('active_group'):
                LENSE.REQUEST.SESSION.set('active_group', groups[0])
                
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