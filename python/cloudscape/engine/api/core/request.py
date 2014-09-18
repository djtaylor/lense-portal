import os
import re
import json
import importlib

# Django Libraries
from django.http import HttpResponse, HttpResponseServerError

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.vars import T_BASE
from cloudscape.engine.api.base import APIBase
from cloudscape.common.utils import JSONTemplate
from cloudscape.common.errors import JSONError, JSONException
from cloudscape.engine.api.auth.key import APIKey
from cloudscape.engine.api.auth.acl import ACLGateway
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.auth.token import APIToken
from cloudscape.engine.api.app.auth.models import DBAuthEndpoints
from cloudscape.engine.api.app.user.models import DBUser

# Configuration / Logger
CONF = config.parse()
LOG  = logger.create(__name__, CONF.server.log)

def dispatch(request):
    """
    The entry point for all API requests. Called for all endpoints from the Django
    URLs file. Creates a new instance of the EndpointManager class, and returns any
    HTTP response to the client that opened the API request.
    
    :param request: The Django request object
    :type request: object
    :rtype: object
    """
    try:
        
        # Return the response from the endpoint handler
        return EndpointManager(request).handler()
    
    # Critical server error
    except Exception as e:
        return JSONException().response()
  
class EndpointManager:
    """
    The endpoint request manager class. Serves as the entry point for all API request,
    both for authentication requests, and already authenticated requests. Constructs
    the base API class, loads API utilities, and performs a number of other functions
    to prepare the API for the incoming request.
    
    The EndpointManager class is instantiated by the dispatch method, which is called
    by the Django URLs module file. It is initialized with the Django request object.
    """
    def __init__(self, request):
        self.request_raw = request
        
        # Request properties
        self.method      = None
        self.request     = None
        self.endpoint    = None
        self.action      = None
        self.path        = None
    
        # Request endpoint handler
        self.handler_obj = None
    
        # API parameters
        self.api_name    = None
        self.api_mod     = None
        self.api_class   = None
        self.api_user    = None
        self.api_group   = None
    
        # API base object
        self.api_base    = None
    
    # Request error
    def _req_error(self, err):
        err_response = {
            'message':  'An error occured when processing the API request',
            'endpoint': self.endpoint,
            'error':    err
        }
        LOG.error('%s:%s' % (self.endpoint, err))
        return HttpResponse(json.dumps(err_response), content_type='application/json', status=400)
    
    def _authenticate(self):
        """
        Authenticate the API request.
        """
        
        # Set the API user and group
        self.api_user  = self.request['api_user']
        self.api_group = None if not ('api_group' in self.request) else self.request['api_group']
        LOG.info('Authenticating API user: %s, group=%s' % (self.api_user, repr(self.api_group)))
        
        # Authenticate key for token requests
        if self.endpoint == 'auth/get':
            auth_status = APIKey().validate(self.request)
            
            # API key authentication failed
            if not auth_status['valid']:
                return JSONError(error='Invalid API key', code=401).response()
            
            # API key authentication successfull
            LOG.info('API key authentication successfull for user: %s' % self.api_user)
            
        # Authenticate token for API requests
        else:
            
            # Invalid API token
            if not APIToken().validate(self.request):
                return JSONError(error='Invalid API token', code=401).response()
            
            # API token looks good
            LOG.info('API token authentication successfull for user: %s' % self.api_user)
    
        # Check for a user account
        if DBUser.objects.filter(username=self.api_user).count():
            
            # If no API group was supplied
            if not self.api_group:
                return JSONError(error='Must submit a group UUID using the [api_group] parameter', code=401).response()
            
            # Make sure the group exists and the user is a member
            is_member = False
            for group in DBUser.objects.filter(username=self.api_user).values()[0]['groups']:
                if group['uuid'] == self.api_group:
                    is_member = True
                    break
            
            # If the user is not a member of the group
            if not is_member:
                return JSONError(error='API user [%s] is not a member of group [%s]' % (self.api_user, self.api_group), code=401).response()
    
    # Validate the request
    def _validate(self):
        
        # Request body / method
        self.request = json.loads(self.request_raw.body)
        self.method  = self.request_raw.META['REQUEST_METHOD']
    
        # Make sure a request action is set
        if not 'action' in self.request:
            return JSONError(error='Request body requires an [action] parameter for endpoint pathing', code=400)
        
        # Set the request action
        self.action = self.request['action']
    
        # Get the request path
        self.path     = re.compile('^\/(.*$)').sub(r'\g<1>', self.request_raw.META['PATH_INFO'])
        
        # Set the request endpoint
        self.endpoint = '%s/%s' % (self.path, self.action)
    
        # Map the path to a module, class, and API name
        self.handler_obj = EndpointMapper(self.endpoint, self.method).handler()
        if not self.handler_obj['valid']:
            return JSONError(error=self.handler_obj['content'], code=400).response()
    
        # Validate the request body
        request_err  = JSONTemplate(self.handler_obj['content']['api_map']).validate(self.request)
        if request_err:
            return JSONError(error=request_err, code=400).response()
    
        # Set the handler objects
        self.api_name    = self.handler_obj['content']['api_name']
        self.api_mod     = self.handler_obj['content']['api_mod']
        self.api_class   = self.handler_obj['content']['api_class']
        self.api_utils   = self.handler_obj['content']['api_utils']
    
    def handler(self):
        """
        The endpoint manager request handler. Performs a number of validation steps before
        passing off the request to the API utility class.
        
        1.) Looks for the base required request parameters
        2.) Maps the endpoint and request action to an API utility and validates the request body
        3.) Authenticates the user and API key/token
        4.) Initializes any required Socket.IO connections for web clients
        5.) Launches the API utility class to process the request
        6.) Returns either an HTTP response with the status of the request
        """
        
        # Validate the request
        try:
            validate_err = self._validate()
            if validate_err:
                return validate_err
            
        # Critical error when validating the request
        except Exception as e:
            return JSONException().response()
        
        # Authenticate the request
        try:
            auth_err     = self._authenticate()
            if auth_err:
                return auth_err
            
        # Critical error when authenticating the request
        except Exception as e:
            return JSONException().response()
        
        # Check the request against ACLs
        acl_gateway = ACLGateway(self.request, self.endpoint, self.api_user)
        
        # If the user is not authorized for this endpoint/object combination
        if not acl_gateway.authorized:
            return JSONError(error=acl_gateway.auth_error, code=401).response()
        
        # Set up the API base
        try:
            
            # Create an instance of the APIBase and run the constructor
            api_obj = APIBase(
                name     = self.api_name, 
                endpoint = self.endpoint, 
                utils    = self.api_utils,
                acl      = acl_gateway
            ).construct(self.request_raw)
            
            # Make sure the construct ran successfully
            if not api_obj['valid']:
                return api_obj['content']
            
            # Set the API base object for endpoint utilities
            self.api_base = api_obj['content']
            
        # Failed to setup the APIBase
        except Exception as e:
            return JSONException().response()
            
        # Load the handler module and class
        handler_mod   = importlib.import_module(self.api_mod)
        handler_class = getattr(handler_mod, self.api_class)
        handler_inst  = handler_class(self.api_base)
        
        # Launch the request handler and return the response
        try:
            response = handler_inst.launch()
            
        # Critical error when running handler
        except Exception as e:
            return JSONException().response()
        
        # Close any open SocketIO connections
        self.api_base.socket.disconnect()
        
        # Return either a valid or invalid request response
        if response['valid']:
            return self.api_base.log.success(response['content'], response['data'])
        return self.api_base.log.error(code=response['code'], log_msg=response['content'])
    
class EndpointMapper:
    """
    API class used to construct the endpoint map. Scans the endpoint request templates
    in the API templates directory to construct a map used to load required utilities
    and modules, as well as validate the request for each endpoint. Each map also contains
    ACL parameters used when constructing the ACL database tables.
    """
    def __init__(self, endpoint=None, method=None):
        """
        Construct the EndpointMapper class.
        
        @param endpoint: The endpoint path
        @type  endpoint: str
        @param method:   The request method
        @type  method:   str
        """
        self.endpoint = endpoint
        self.method   = method
        self.map      = {}
        
    def _merge_auth(self,j,e):
        """
        Helper method used to merge token authentication parameters into the endpoint
        request map. Mainly so I don't have to redundantly include the same code in
        every map. Also makes modification much easier.
        """
        
        # Ignore the authentication endpoint, as this is used to retrieve the token
        if e == 'auth/get':
            return
        
        # Required / optional  connection parameters
        j['root']['_required'].extend(['api_user', 'api_token', 'action'])
        j['root']['_optional'].extend(['api_group'])
        
        # Connection parameter types
        t = { 'api_user': 'str', 'api_token': 'str', 'action': 'str', 'api_group': 'uuid4' }
        for k,v in t.iteritems():
            j['root']['_children'][k] = { '_type': v }
        
    def _merge_socket(self,j):
        """
        Merge request parameters for web socket request. Used for handling connections
        being passed along by the Socket.IO API proxy.
        """
        
        # Load the socket request validator map
        sv = json.loads(open('%s/socket.json' % T_BASE, 'r').read())
        
        # Make sure the '_children' key exists
        if not '_children' in j['root']:
            j['root']['_children'] = {}
        
        # Merge the socket parameters map
        j['root']['_children']['socket'] = sv
        j['root']['_optional'].append('socket')
        
    def _build_map(self):
        """
        Load all endpoint definitions.
        """
        for endpoint in list(DBAuthEndpoints.objects.all().values()):
            
            # Try to load the request map
            try:
                endpoint_rmap = json.loads(endpoint['rmap'])
            
                # Map base object
                rmap_base = {
                    'root': endpoint_rmap
                }
                
                # Merge the web socket request validator
                self._merge_socket(rmap_base)
                
                # Merge the authentication request validation parameters
                self._merge_auth(rmap_base, endpoint['name'])
            
                # Load the endpoint request handler module string
                self.map[endpoint['name']] = {
                    'module': endpoint['mod'],
                    'class':  endpoint['cls'],
                    'name':   endpoint['name'],
                    'desc':   endpoint['desc'],
                    'method': endpoint['method'],
                    'utils':  None if not endpoint['utils'] else json.loads(endpoint['utils']),
                    'json':   rmap_base
                }
            
            # Error constructing request map, skip to next endpoint map
            except Exception as e:
                LOG.exception('Failed to load request map for endpoint [%s]: %s ' % (endpoint['name'], str(e)))
                continue
                    
        # All template maps constructed
        return valid(LOG.info('Constructed API template map'))
        
    def handler(self):
        """
        Main method for constructing and returning the endpoint map.
        
        @return valid|invalid
        """
        map_rsp = self._build_map()
        if not map_rsp['valid']:
            return map_rsp
        
        # Request endpoint missing
        if not self.endpoint:
            return invalid(JSONError(error='Missing request endpoint', code=400).response())
        
        # Invalid request path
        if not self.endpoint in self.map:
            return invalid(JSONError(error='Unsupported request endpoint: [%s]' % self.endpoint, code=400).response())
        
        # Verify the request method
        if self.method != self.map[self.endpoint]['method']:
            return invalid(JSONError(error='Unsupported request method [%s] for endpoint [%s]' % (self.method, self.endpoint), code=400).response())
        
        # Get the API module, class handler, and name
        self.handler_obj = {
            'api_mod':   self.map[self.endpoint]['module'],
            'api_class': self.map[self.endpoint]['class'],
            'api_name':  self.map[self.endpoint]['name'],
            'api_utils': self.map[self.endpoint]['utils'],
            'api_map':   self.map[self.endpoint]['json']
        }
        LOG.info('Parsed handler object for API endpoint [%s]: %s' % (self.endpoint, self.handler_obj))
        
        # Return the handler module path
        return valid(self.handler_obj)