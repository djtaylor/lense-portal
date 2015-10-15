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
from lense import MODULE_ROOT
from lense.common import config
from lense.common import logger
from lense.portal.ui.base import PortalBase

# Module class name
MOD_CLASS = 'AppModule'

# Configuration / Logger
CONF = config.parse('PORTAL')
LOG  = logger.create(__name__, CONF.portal.log)

def dispatch(request):
    """
    Method used to handle incoming portal requests.
    """
    try:
        
        # Return the response from the endpoint handler
        return RequestManager(request).handler()
    
    # Critical server error
    except Exception as e:
        LOG.exception('Internal server error: {0}'.format(str(e)))
            
        # Get the exception data
        e_type, e_info, e_trace = sys.exc_info()
            
        # Format the exception message
        e_msg = '{0}: {1}'.format(e_type.__name__, e_info)
            
        # Load the error template
        t = loader.get_template('core/error/500.html')
        
        # Return a server error
        return HttpResponseServerError(t.render(RequestContext(request, {
            'error': 'An error occurred when rendering the requested page.',
            'debug': None if not CONF.portal.debug else (e_msg, reversed(traceback.extract_tb(e_trace)))
        })))
    
class RequestManager(object):
    """
    Handle requests passed off by the dispatch handler.
    """
    def __init__(self, request):
        
        # Construct the request object
        self.request = request
        
        # Request path / available applications
        self.path    = self.request.META['PATH_INFO'].replace('/', '')
        self.apps    = self._load_applications()
        
    def _load_applications(self):
        """
        Load all available applications.
        """
        
        # Module directory / base path
        app_path = '{0}/portal/ui/app'.format(MODULE_ROOT)
        app_base = 'cloudscape.portal.ui.app'
        
        # Applications object
        app_obj  = {}
        
        # Scan every application
        for app in os.listdir(app_path):
            
            # Ignore special files
            if re.match(r'^__.*$', app) or re.match(r'^.*\.pyc$', app):
                continue
            
            # Define the application view module
            app_view = '{0}/{1}/views.py'.format(app_path, app)
            
            # If the application has a view associated with it
            if os.path.isfile(app_view):
                mod_path = '{0}.{1}.views'.format(app_base, app)
                
                # Create a new module instance
                mod_obj  = importlib.import_module(mod_path)
                cls_obj  = getattr(mod_obj, MOD_CLASS)
                
                # Add to the modules object
                app_obj[app] = cls_obj
                
                # Load application module
                LOG.info('Loading application module: app={0}, module={1}'.format(app, mod_path))
        
        # Return the constructed applications object
        return app_obj
        
    def redirect(self, path):
        """
        Return an HTTPResponseRedirect object.
        """
        return HttpResponseRedirect('/{0}'.format(path))
        
    def handler(self):
        """
        Worker method for mapping requests to controllers.
        """
        
        # If the path doesn't point to a valid application
        if not self.path in self.apps:
            return self.redirect('auth')
        
        # Load the application
        return self.apps[self.path].as_view(portal=PortalBase(__name__).construct(self.request))(self.request)