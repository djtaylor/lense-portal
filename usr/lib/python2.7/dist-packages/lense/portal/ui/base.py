import os
import re
import json
import copy
import importlib

# Django Libraries
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponseServerError

# Lense Libraries
from lense.portal.ui.core.api import APIClient
from lense.common.request import LenseRequestObject
from lense.common.objects.user.models import APIUser

class PortalBase(object):
    """
    Base class shared by all Lense portal views. This is used to initialize
    requests, construct template data, set the logger, etc.
    """
    def __init__(self):
        
        # API objects / application controllers
        self.api           = None
        self.controller    = LENSE.MODULE.handlers(ext='controller', load='HandlerController')
       
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
                    # Grab the response body
                    _body = response['body']
                    
                    # If returned as a string
                    if isinstance(_body, str):
                        return json.loads(response['body'])
                    return _body
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
        return LENSE.COLLECTION(api_obj).get()
           
    def api_call(self, module, method, data=None):
        """
        Wrapper method for the APIClient class instance.
        """
        
        # Make sure the base attribute exists
        if hasattr(self.portal.api.client, module):
            api_base = getattr(self.portal.api.client, module)
            
            # Make sure the method attribute exists
            if hasattr(api_base, method):
                api_method = getattr(api_base, method)
       
                # Run the API request and return a filtered response
                return self.filter.object(self.portal.api.response(api_method(data))).map('{0}.{1}'.format(module, method))
       
        # Invalid base/method attribute
        return False    
        
    def _set_session(self):
        """
        Set session variables.
        """
        if LENSE.REQUEST.user.authorized:
            
            # Get the user details
            _user = LENSE.USER.get(LENSE.REQUEST.user.name)
            
            # Set the 'is_admin' flag
            LENSE.REQUEST.SESSION.set('is_admin', user_details['is_admin'])
            
            # If the active group hasn't been set yet
            if not LENSE.REQUEST.SESSION.get('active_group'):
                LENSE.REQUEST.SESSION.set('active_group', _user['groups'][0]['uuid'])
        
    def _run_controller(self, **kwargs):
        """
        Run the target application controller.
        """
        
        # If the user is authenticated
        if LENSE.REQUEST.user.authorized:
            
            # Redirect to home page if trying to access the login screen
            if LENSE.REQUEST.path == 'auth':
                return LENSE.HTTP.redirect('home')
            
            # Return the template response
            return self.controller[LENSE.REQUEST.path](self).construct(**kwargs)
            
        # User is not authenticated
        else:
            
            # Redirect to the login screen if trying to access any other page
            if not LENSE.REQUEST.path == 'auth':
                return LENSE.HTTP.REDIRECT('auth')
            
            # Return the template response
            return self.controller[LENSE.REQUEST.path](self).construct(**kwargs)
        
    def set_active_group(self, group):
        """
        Change the session variable for the active API user group.
        """
        
        # Get all user groups
        all_groups = APIUser.objects.filter(username=self.request.user).values()[0]['groups']
        
        # Make sure the user is a member of the group
        is_member = False
        for _group in all_groups:
            if _group['uuid'] == group:
                is_member = True
                break 
        
        # If the group is valid
        if is_member:
            self.request_raw.session['active_group'] = group
        
    def login(self, username, password):
        """
        Login a user account.
        """
        
        # User exists and is authenticated
        if LENSE.USER.AUTHENTICATE(user=username, password=password):
            
            # User is active
            if LENSE.REQUEST.user.active:
                LENSE.LOG.info('User account [{0}] active, logging in user'.format(username))
                
                # Login the user account
                LENSE.USER.LOGIN(LENSE.REQUEST.DJANGO, username)
                
                # Redirect to the home page
                return LENSE.HTTP.redirect('/home')
            
            # User account is inactive
            else:
                LENSE.LOG.info('Login failed, user account "{0}" is inactive'.format(username))
                state = 'Your account is disabled - please contact your administrator'
        
        # User account does not exist or username/password incorrect
        else:
            LENSE.LOG.error('Login failed, user account "{0}" does not exist or password is incorrect'.format(username))
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
        
    def construct(self, request):
        """
        Construct the portal request and template data. Set the user authentication parameter,
        construct the request object, API connector, template data, and return the portal
        base object.
        """
        
        # Bootstrap the session
        self._set_session()
        
        # If the user is authenticated
        if LENSE.REQUEST.user.authorized:
            
            # Set the API connector
            self.api = self._set_api()
        
            # Set all available groups
            self.api.params['groups'] = self.user['groups']
            
            # Process each API parameter
            for key,value in self.api.params.iteritems():
                if isinstance(value, list) or isinstance(value, dict):
                    continue
                self.api.params[key] = value
        
        # Construct and return the application template
        self.template = self._run_controller()
        
        # Return the constructed portal base
        return self