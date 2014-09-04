import os
import re
import json
import copy
import importlib

# Django Libraries
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponseServerError

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.vars import L_BASE
from cloudscape.portal.ui.core.api import APIClient
from cloudscape.common.collection import Collection
from cloudscape.engine.api.app.user.models import DBUserDetails

class AppBase(View):
    """
    Base class used by application view modules.
    """
    def __init__(self, request):
        
        # Construct the base portal object
        self.portal = PortalBase(__name__).construct(request)

    def redirect(self, path):
        """
        Return an HTTPResponseRedirect object.
        """
        return HttpResponseRedirect('/%s' % path)

class PortalBase(object):
    """
    Base class shared by all CloudScape portal views. This is used to initialize
    requests, construct template data, set the logger, etc.
    """
    def __init__(self, name):
        self.class_name    = 'cloudscape' if not name else name
        
        # Authentication flag
        self.authenticated = False
        
        # Raw request
        self.request_raw   = None
        
        # Request / API objects / application controllers
        self.request       = None
        self.api           = None
        self.app           = {}
        
        # User groups
        self.groups        = None
        
        # Initialize the configuration object and logger
        self.conf          = config.parse()
        self.log           = logger.create(self.class_name, self.conf.portal.log)
       
    def _api_response(self, response, type='json'):
        """
        Parse the response code and body from an API response.
        """
        
        # Make sure a response code and body are set
        if not 'code' in response or not 'body' in response:
            return None
        
        # Parse a JSON response
        if type == 'json':
            if response['code'] == 200:
                try:
                    return json.loads(response['body'])
                except:
                    return {}
            return {}
        else:
            return None
       
    def _set_api(self, session):
        """
        Setup the API client.
        """
        
        # Construct the API connector and connection parameters
        connector, params = APIClient().get(self.request.user, self.request.group)
        if not connector or not params:
            return False
        
        # Append the session ID to the API parameters
        params['session'] = session;
        
        # Define the API object
        api_obj = {
            'client':   connector,
            'params':   params,
            'response': self._api_response
            
        }
        return Collection(api_obj).get()
        
    def _set_url(self, path):
        return '%s://%s:%s/%s' % (self.conf.portal.proto, self.conf.portal.host, self.conf.portal.port, path)
        
    def _set_app_controllers(self):
        """
        Construct supported application controllers.
        """
        
        # Application directory / module base
        app_dir  = '%s/python/cloudscape/portal/ui/app' % L_BASE
        mod_base = 'cloudscape.portal.ui.app'
        
        # Scan every application
        for app_name in [x for x in os.listdir(app_dir) if not re.match(r'__|pyc', x)]:
            controller = '%s/%s/controller.py' % (app_dir, app_name)
            
            # If a controller module exists
            if os.path.isfile(controller):
                
                # Load the controller
                try:
                    
                    # Define the module name
                    mod_name = '%s.%s.controller' % (mod_base, app_name)
                    
                    # Create a new module instance
                    mod_obj  = importlib.import_module(mod_name)
                    cls_obj  = getattr(mod_obj, 'AppController')
                    
                    # Add to the application object
                    self.app[app_name] = cls_obj
                    
                # Critical error when loading controller
                except Exception as e:
                    self.log.exception('Failed to load application <%s> controller: %s' % (app_name, str(e)))
                    
                    # Application controller disabled
                    self.app[app_name] = False
        
    def _set_request(self, request):
        """
        Setup the incoming request object.
        """
        self.request_raw = request
        
        # If the active group session variable hasn't been set yet
        if request.user.is_authenticated():
            
            # Get all user groups
            all_groups = DBUserDetails.objects.get(username=request.user.username).get_groups()
            
            # If the active group hasn't been set yet
            if not 'active_group' in request.session:
            
                # Set the active group to the first available group
                request.session['active_group'] = all_groups[0]['uuid']
        
        # Get the request method
        method = request.META['REQUEST_METHOD']
        
        # Set available groups
        self.groups = None if not request.user.is_authenticated() else all_groups
        
        # Define the request object
        request_obj = {
            'method':  method,
            'get':     None if not method == 'GET' else request.GET,
            'post':    None if not method == 'POST' else request.POST,
            'session': None if not hasattr(request, 'session') else request.session.session_key,
            'user':    None if not hasattr(request, 'user') else request.user.username,
            'body':    request.body,
            'path':    request.META['PATH_INFO'].replace('/',''),
            'query':   request.META['QUERY_STRING'],
            'script':  request.META['SCRIPT_NAME'],
            'group':   None if not request.user.is_authenticated() else request.session['active_group'],
            'current': request.META['REQUEST_URI']
        }
        
        # Return a request collection
        return Collection(request_obj).get()
        
    def _run_application(self):
        """
        Run the target application.
        """
        
        # If the user is authenticated
        if self.authenticated:
            
            # Redirect to home page if trying to access the login screen
            if self.request.path == 'auth':
                return HttpResponseRedirect(self._set_url('home'))
            
            # Return the template response
            return self.app[self.request.path](self).construct()
            
        # User is not authenticated
        else:
            
            # Redirect to the authentication screen if trying to access any other page
            if not self.request.path == 'auth':
                return HttpResponseRedirect(self._set_url('auth'))
            
            # Return the template response
            return self.app[self.request.path](self).construct()
        
    def set_active_group(self, group):
        """
        Change the session variable for the active API user group.
        """
        
        # Get all user groups
        all_groups = DBUserDetails.objects.get(username=self.request.user).get_groups()
        
        # Make sure the user is a member of the group
        is_member = False
        for _group in all_groups:
            if _group['uuid'] == group:
                is_member = True
                break 
        
        # If the group is valid
        if is_member:
            self.request_raw.session['active_group'] = group
        
    def construct(self, request):
        """
        Construct the portal request and template data. Set the user authentication parameter,
        construct the request object, API connector, template data, and return the portal
        base object.
        """
        
        # Construct request object
        self.request = self._set_request(request)
        
        # If the user is authenticated
        if request.user.is_authenticated():
            self.authenticated = True
            
            # Set the API connector
            self.api = self._set_api(self.request.session)
        
            # Set all available groups
            self.api.params['groups'] = self.groups
            
            # Process each API parameter
            for key,value in self.api.params.iteritems():
                if isinstance(value, list) or isinstance(value, dict):
                    continue
                self.api.params[key] = value
        
        # Construct application controllers
        self._set_app_controllers()
        
        # Construct and return the application template
        self.template = self._run_application()
        
        # Return the constructed portal base
        return self