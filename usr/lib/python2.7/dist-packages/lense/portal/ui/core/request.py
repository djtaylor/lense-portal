import sys
import traceback

# Lense Libraries
from lense.portal.ui.base import PortalBase
from lense.common.exceptions import EnsureError, AuthError, RequestError

def dispatch(request):
    """
    Method used to handle incoming portal requests.
    """
    LENSE.SETUP.portal(request)
    
    # Run the request dispatcher
    try:
        
        # Return the response from the endpoint handler
        return RequestManager.dispatch(request)
    
    # Critical server error
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
    
class RequestManager(object):
    """
    Handle requests passed off by the dispatch handler.
    """
    def run(self):
        """
        Public method for running the portal request.
        """
        
        # If the path doesn't point to a valid handler
        if not LENSE.REQUEST.path in LENSE.PORTAL.handlers:
            return LENSE.HTTP.redirect('auth')
        
        # Load the application
        return LENSE.PORTAL.handlers[LENSE.REQUEST.path].as_view()
    
    @classmethod
    def dispatch(cls, request):
        """
        Class method for dispatching the incoming WSGI request object.
        """
        try:
            return cls().run()
        
        # Internal request error
        except (EnsureError, AuthError, RequestError) as e:
            LENSE.LOG.exception(e.message)
            
            # Error template
            template = 'core/error/{0}.html'.format(e.code)
            
            # Return a browser error
            return LENSE.HTTP.browser_error(template, {
                'error': e.message
            })
            