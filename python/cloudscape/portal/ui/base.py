import os
import re
import json
import copy
import importlib

# Django Libraries
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponseServerError

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.vars import L_BASE
from cloudscape.portal.ui.core.api import APIClient
from cloudscape.common.collection import Collection
from cloudscape.engine.api.app.user.models import DBUser

class PortalRequest(object):
    """
    Construct and return a portal request object.
    """
    def __init__(self, request):
        
        # Raw request object
        self.RAW      = request
        
        # Method / GET / POST / body data
        self.method   = request.META['REQUEST_METHOD']
        self.GET      = Collection(request.GET).get()
        self.POST     = Collection(request.POST).get()
        self.body     = request.body
        
        # User / group / session
        self.user     = None if not hasattr(request, 'user') else request.user.username
        self.group    = None if not request.user.is_authenticated() else request.session['active_group']
        self.session  = None if not hasattr(request, 'session') else request.session.session_key
        self.is_admin = False if not request.user.is_authenticated() else request.session['is_admin']
        
        # Path / query string / script / current URI
        self.path     = request.META['PATH_INFO'].replace('/','')
        self.query    = request.META['QUERY_STRING']
        self.script   = request.META['SCRIPT_NAME']
        self.current  = request.META['REQUEST_URI']

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
        self.controller    = {}
        
        # User object
        self.user          = None
        
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
       
    def _set_api(self):
        """
        Setup the API client.
        """
        
        # Construct the API connector and connection parameters
        connector, params = APIClient().get(self.request.user, self.request.group)
        if not connector or not params:
            return False
        
        # Append the session ID to the API parameters as well as the 'is_admin' flag
        params.update({
            'session': self.request.session,
            'is_admin': self.request.is_admin
        })
        
        # Define the API object
        api_obj = {
            'client':   connector,
            'params':   params,
            'response': self._api_response,
            'is_admin': self.request.is_admin
            
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
                    self.controller[app_name] = cls_obj
                    
                # Critical error when loading controller
                except Exception as e:
                    self.log.exception('Failed to load application <%s> controller: %s' % (app_name, str(e)))
                    
                    # Application controller disabled
                    self.controller[app_name] = False
        
    def _set_request(self, request):
        """
        Setup the incoming request object.
        """
        
        # If the active group session variable hasn't been set yet
        if request.user.is_authenticated():
            
            # Get the user details
            user_details = DBUser.objects.filter(username=request.user.username).values()[0]
            
            # Set the user's groups
            self.user = user_details
            
            # Set the 'is_admin' flag
            request.session['is_admin'] = user_details['is_admin']
            
            # If the active group hasn't been set yet
            if not 'active_group' in request.session:
            
                # Set the active group to the first available group
                request.session['active_group'] = user_details['groups'][0]['uuid']
        
        # Return a request object
        return PortalRequest(request)
        
    def _run_controller(self, **kwargs):
        """
        Run the target application controller.
        """
        
        # If the user is authenticated
        if self.authenticated:
            
            # Redirect to home page if trying to access the login screen
            if self.request.path == 'auth':
                return HttpResponseRedirect(self._set_url('home'))
            
            # Return the template response
            return self.controller[self.request.path](self).construct(**kwargs)
            
        # User is not authenticated
        else:
            
            # Redirect to the authentication screen if trying to access any other page
            if not self.request.path == 'auth':
                return HttpResponseRedirect(self._set_url('auth'))
            
            # Return the template response
            return self.controller[self.request.path](self).construct(**kwargs)
        
    def set_active_group(self, group):
        """
        Change the session variable for the active API user group.
        """
        
        # Get all user groups
        all_groups = DBUser.objects.filter(username=self.request.user).values()[0]['groups']
        
        # Make sure the user is a member of the group
        is_member = False
        for _group in all_groups:
            if _group['uuid'] == group:
                is_member = True
                break 
        
        # If the group is valid
        if is_member:
            self.request_raw.session['active_group'] = group
        
    def GET(self, key, default=False):
        """
        Look for data in the request GET object.
        """
        if hasattr(self.request.GET, key):
            return getattr(self.request.GET, key)
        return default
        
    def POST(self, key, default=False):
        """
        Look for data in the request POST object.
        """
        if hasattr(self.request.POST, key):
            return getattr(self.request.POST, key)
        return default
        
    def login(self, username, password):
        """
        Login a user account.
        """
            
        # Attempt to authenticate the user
        user = authenticate(username=username, password=password)
        
        # User exists and is authenticated
        if user is not None:
            
            # User is active
            if user.is_active:
                self.log.info('User account [%s] active, logging in user' % username)
                
                # Login the user account
                login(self.request.RAW, user)
                
                # Redirect to the home page
                return self.redirect('/home')
            
            # User account is inactive
            else:
                self.log.info('Login failed, user account [%s] is inactive' % username)
                state = 'Your account is not active - please contact your administrator'
        
        # User account does not exist or username/password incorrect
        else:
            self.log.error('Login failed, user account [%s] does not exist or password is incorrect' % username)
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
        
    def redirect(self, path):
        """
        Wrapper method for the HTTPResponseRedirect class
        """
        return HttpResponseRedirect(path)
        
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
            self.api = self._set_api()
        
            # Set all available groups
            self.api.params['groups'] = self.user['groups']
            
            # Process each API parameter
            for key,value in self.api.params.iteritems():
                if isinstance(value, list) or isinstance(value, dict):
                    continue
                self.api.params[key] = value
        
        # Construct application controllers
        self._set_app_controllers()
        
        # Construct and return the application template
        self.template = self._run_controller()
        
        # Return the constructed portal base
        return self