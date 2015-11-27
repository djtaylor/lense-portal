import os
import re
import sys
import json
import importlib
import traceback

# Django Libraries
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect

# Lense Libraries
from lense.common import LenseCommon
from lense.portal.ui.base import PortalBase

# Lense Common
LENSE = LenseCommon('PORTAL')

def dispatch(request):
    """
    Method used to handle incoming portal requests.
    """
    try:
        
        LENSE.LOG.info('USER: {0}'.format(dir(request.user)))
        
        # Return the response from the endpoint handler
        return RequestManager(request).handler()
    
    # Critical server error
    except Exception as e:
        LENSE.LOG.exception('Internal server error: {0}'.format(str(e)))
            
        # Get the exception data
        e_type, e_info, e_trace = sys.exc_info()
            
        # Format the exception message
        e_msg = '{0}: {1}'.format(e_type.__name__, e_info)
            
        # Load the error template
        t = loader.get_template('core/error/500.html')
        
        # Return a server error
        return HttpResponseServerError(t.render(RequestContext(request, {
            'error': 'An error occurred when rendering the requested page.',
            'debug': None if not LENSE.CONF.portal.debug else (e_msg, reversed(traceback.extract_tb(e_trace)))
        })))
    
class RequestManager(object):
    """
    Handle requests passed off by the dispatch handler.
    """
    def __init__(self, request):
        
        # Store the request object
        self.request  = LENSE.REQUEST.SET(request)
        
        # Request path / available handlers
        self.path     = self.request.path.replace('/', '')
        self.handlers = self._load_handlers()
        
    def _load_handlers(self):
        """
        Load all available request handlers.
        """
        
        # Handler file path / module base
        handler_files = '{0}/portal/ui/handlers'.format(LENSE.MODULE.ROOT)
        handler_mods  = 'lense.portal.ui.handlers'
        
        # Handlers object
        handler_obj   = {}
        
        # Scan every handler
        for handler in os.listdir(handler_files):
            
            # Ignore special files
            if re.match(r'^__.*$', handler) or re.match(r'^.*\.pyc$', handler):
                continue
            
            # Define the handler view module
            handler_view = '{0}/{1}/views.py'.format(handler_files, handler)
            
            # If the handler has a view associated with it
            if os.path.isfile(handler_view):
                mod_path = '{0}.{1}.views'.format(handler_mods, handler)
                
                # Create a new module instance
                mod_obj  = importlib.import_module(mod_path)
                cls_obj  = getattr(mod_obj, 'HandlerView')
                
                # Add to the handlers object
                handler_obj[handler] = cls_obj
                
                # Load handler module
                LENSE.LOG.info('Loading request handler view: path={0}, module={1}'.format(handler, mod_path))
        
        # Return the constructed handlers object
        return handler_obj
        
    def redirect(self, path):
        """
        Return an HTTPResponseRedirect object.
        """
        return HttpResponseRedirect('/{0}'.format(path))
        
    def handler(self):
        """
        Worker method for mapping requests to controllers.
        """
        
        # If the path doesn't point to a valid handler
        if not self.path in self.handlers:
            return self.redirect('auth')
        
        # Load the application
        return self.handlers[self.path].as_view(portal=PortalBase().construct(self.request))(self.request)