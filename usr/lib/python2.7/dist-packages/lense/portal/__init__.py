from sys import exc_info
from traceback import extract_tb
from django.shortcuts import render

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

class PortalTemplate(PortalBase):
    """
    Class for handling Django template attributes and functionality.
    """
    def __init__(self):
        
        # User defined template data / requesting user object
        self.data = None
        self.user = LENSE.OBJECTS.USER.get(**{'username': LENSE.REQUEST.USER.name})
        
    def construct(self, data):
        """
        Construct portal template attributes.
        """
        self.data = self._merge_data(data)

    def _user_data(self):
        """
        Construct and return user data.
        """
        return {
            'is_admin': LENSE.REQUEST.USER.admin,
            'is_authenticated': LENSE.REQUEST.USER.authorized,
            'groups': getattr(self.user, 'groups', None),
            'email': getattr(self.user, 'email', None)
        }

    def _request_data(self):
        """
        Construct and return request data.
        """
        return {
            'current': LENSE.REQUEST.current,
            'path': LENSE.REQUEST.path,
            'base': LENSE.REQUEST.script
        }

    def _api_data(self):
        """
        Construct and return API data.
        """
        return {
            'user': getattr(self.user, 'username', None),
            'group': getattr(self.user, 'groups', None),
            'key': getattr(self.user, 'api_key', None),
            'token': getattr(self.user, 'api_token', None),
            'endpoint': '{0}://{1}:{2}'.format(LENSE.CONF.engine.proto, LENSE.CONF.engine.host, LENSE.CONF.engine.port)
        }

    def _merge_data(self, data={}):
        """
        Merge base template data and page specific template data. 
        """
        
        # Base parameters
        params = {
            'USER': self._user_data(),
            'REQUEST': self._request_data(),
            'API': self._api_data()
        }
        
        # Log base template data
        self.log('Constructing base template data: USER={0}, REQUEST={1}, API={2}'.format(params['USER'], params['REQUEST'], params['API']), level='debug', method='_merge_data')
        
        # Merge extra template parameters
        for k,v in data.iteritems():
            
            # Do not overwrite the 'BASE' key
            if k in ['USER','REQUEST','API']:
                raise RequestError('Template data key "{0}" cannot be overloaded'.format(k), code=500)
            
            # Append the template data key
            params[k] = v
            self.log('Appending template data: key={0}, value={1}'.format(k,v), level='debug', method='_merge_data')
            
        # Return the template data object
        return params

    def response(self):
        """
        Construct and return the template response.
        """
        
        # If redirecting
        if 'redirect' in self.data:
            self.log('Redirecting -> {0}'.format(self.data['redirect']), level='debug', method='response')
            return LENSE.HTTP.redirect(self.data['redirect'])
        
        # Return the template response
        try:
            self.log('Return response: interface.html, data={0}'.format(self.data), level='debug', method='response')
            return render(LENSE.REQUEST.DJANGO, 'interface.html', self.data)
        
        # Failed to render template
        except Exception as e:
            self.log('Internal server error: {0}'.format(str(e)), level='exception', method='response')
            
            # Get the exception data
            e_type, e_info, e_trace = exc_info()
            e_msg = '{0}: {1}'.format(e_type.__name__, e_info)
            
            # Return a server error
            return LENSE.HTTP.browser_error('core/error/500.html', {
                'error': 'An error occurred when rendering the requested page',
                'debug': None if not LENSE.CONF.portal.debug else (e_msg, reversed(extract_tb(e_trace)))
            })

class PortalInterface(PortalBase):
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
        
    def controller(self, **kwargs):
        """
        Run the target application controller.
        """
        
        # If the user is authenticated
        if LENSE.REQUEST.USER.authorized:
            
            # Redirect to home page if trying to access the login screen
            if LENSE.REQUEST.path == 'auth':
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