import os
import sys
import json
import time
import datetime

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'cloudscape.engine.api.core.settings'

# Django Libraries
from django.test.client import RequestFactory

# CloudScape Libraries
import cloudscape.common.config as config
import cloudscape.common.logger as logger
from cloudscape.common.utils import parse_response
import cloudscape.engine.api.core.request as request
from cloudscape.engine.api.app.auth.utils import DBAuthEndpoints
from cloudscape.engine.api.app.user.models import DBUserAPITokens

class ScheduleBase(object):
    """
    Base class used when creating instances of the scheduler modules.
    """
    def __init__(self, name):
        
        # Module name
        self.name       = name
        
        # Configuration and logger
        self.conf       = config.parse()
        self.log        = logger.create(name, self.conf.scheduler.log)
        
        # Internal API user / token
        self.api_user   = None
        self.api_group  = None
        self.api_token  = None
        
        # Time / datetime / JSON module
        self.time       = time
        self.datetime   = datetime
        self.json       = json
        
        # Endpoints
        self.endpoints  = self._load_endpoints()
        
        # Module initialized
        self.log.info('Initialized scheduler module: %s' % name)
        
    def set_api(self, user, group):
        """
        Set the API user and group for internal requests.
        """
        
        # Make sure the user exists and has a token
        if not DBUserAPITokens.objects.filter(user=user).count():
            self.log.error('Failed to set API user <%s>, could not locate in API tokens table' % user)
            sys.exit(1)
        
        # Set the API user and token
        self.api_user  = user
        self.api_group = group
        self.api_token = DBUserAPITokens.objects.filter(user=user).values()[0]['token']
        
    def _load_endpoints(self):
        """
        Load all endpoint objects
        """
        
        # Load all available endpoints
        all_endpoints = list(DBAuthEndpoints.objects.all().values())
        
        # Construct an endpoint object with the name as the key
        endpoint_obj = {}
        for endpoint in all_endpoints:
            endpoint_obj[endpoint['name']] = endpoint
            
        # Set the endpoint object
        return endpoint_obj
        
    def request(self, path, action, data=None):
        """
        Make an internal API request.
        """
        
        # Make sure an API user and token are defined
        if not self.api_user or not self.api_token:
            return self.log.error('Failed to make API request, API user and/or token not set')
        
        # Define the full endpoint
        endpoint = '%s/%s' % (path, action)
        
        # If data is supplied, make sure it is valid
        if data and not isinstance(data, dict):
            return self.log.error('Failed to make API request, request data must be in dictionary format')
        
        # Make sure the endpoint is valid
        if not endpoint in self.endpoints:
            return self.log.error('Failed to make API request, endpoint not found: %s/%s' % (path, action))
        
        # Log the request details
        self.log.info('Submitting API request: endpoint=%s, api_user=%s, data=%s' % (endpoint, self.api_user, ('None' if not data else json.dumps(data))))
        
        # Attempt to construct a new request object
        try:
            
            # Define the request defaults
            defaults = {
                'REQUEST_METHOD': self.endpoints[endpoint]['method'],
                'SERVER_NAME':    self.conf.server.host,
                'PATH_INFO':      '/%s' % path,
                'REQUEST_URI':    '/cloudscape-api/%s' % path,
                'SCRIPT_NAME':    '/cloudscape-api',
                'SERVER_PORT':    '10550',
                'CONTENT_TYPE':   'application/json'
            }
            
            # Create a new instance of the request factory
            rf = RequestFactory(**defaults)
            
            # Construct the request object
            request_obj = rf.request()
            
            # Define the request body
            body = {
                'api_user':  self.api_user,
                'api_token': self.api_token,
                'api_group': self.api_group,
                'action':    action
            }
            
            # If any request data
            if data:
                body['_data'] = data
            
            # Set the request body
            request_obj._body = json.dumps(body)
            
        # Critical error when constructing request object
        except Exception as e:
            self.log.exception('Failed to construct request object: %s' % str(e))
        
        # Dispatch the request and get the response
        response = parse_response(request.dispatch(request_obj))
        
        # Load the response body
        def load_body(body):
            try:
                return json.loads(body)
            except:
                return body
        
        # Return the response
        return {
            'code': response['code'],
            'body': load_body(response['body'])
        }