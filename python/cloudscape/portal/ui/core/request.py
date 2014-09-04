import os
import re
import json
import importlib

# Django Libraries
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.vars import L_BASE

# Module class name
MOD_CLASS = 'AppModule'

# Configuration / Logger
CONF = config.parse()
LOG  = logger.create('cloudscape.portal.ui.core.request', CONF.portal.log)

def dispatch(request):
    """
    Method used to handle incoming portal requests.
    """
    try:
        
        # Return the response from the endpoint handler
        return RequestManager(request).handler()
    
    # Critical server error
    except Exception as e:
        LOG.exception('Internal server error: %s' % str(e))
        
        # Return a 500 error
        return HttpResponseServerError('Internal server error, please contact your administrator.')
    
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
        app_path = '%s/python/cloudscape/portal/ui/app' % L_BASE
        app_base = 'cloudscape.portal.ui.app'
        
        # Applications object
        app_obj  = {}
        
        # Scan every application
        for app in os.listdir(app_path):
            
            # Ignore special files
            if re.match(r'^__.*$', app) or re.match(r'^.*\.pyc$', app):
                continue
            
            # Define the application view module
            app_view = '%s/%s/views.py' % (app_path, app)
            
            # If the application has a view associated with it
            if os.path.isfile(app_view):
                mod_path = '%s.%s.views' % (app_base, app)
                
                # Create a new module instance
                mod_obj  = importlib.import_module(mod_path)
                cls_obj  = getattr(mod_obj, MOD_CLASS)
                
                # Add to the modules object
                app_obj[app] = cls_obj
                
                # Load application module
                LOG.info('Loading application module: app=%s, module=%s' % (app, mod_path))
        
        # Return the constructed applications object
        return app_obj
        
    def redirect(self, path):
        """
        Return an HTTPResponseRedirect object.
        """
        return HttpResponseRedirect('/%s' % path)
        
    def handler(self):
        """
        Worker method for mapping requests to controllers.
        """
        
        # If the path doesn't point to a valid application
        if not self.path in self.apps:
            return self.redirect('auth')
        
        # Load the application
        return self.apps[self.path].as_view()(self.request)