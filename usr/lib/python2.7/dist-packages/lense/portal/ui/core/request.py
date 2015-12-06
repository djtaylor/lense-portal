import os
import re
import sys
import json
import traceback
from importlib import import_module

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
        LENSE.REQUEST.SET(request)
        
        # Request path / available handlers
        self.path     = self.request.path.replace('/', '')
        self.handlers = LENSE.MODULE.HANDLERS(ext='views', load='HandlerView')
        
    def handler(self):
        """
        Worker method for mapping requests to controllers.
        """
        
        # If the path doesn't point to a valid handler
        if not self.path in self.handlers:
            return LENSE.HTTP.redirect('auth')
            
            return self.redirect('auth')
        
        # Load the application
        return self.handlers[self.path].as_view(portal=PortalBase().construct(self.request))(self.request)