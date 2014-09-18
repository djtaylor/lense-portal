import re
import copy
import json
import importlib

# Django Libraries
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.utils import valid, invalid
from cloudscape.common.collection import Collection
from cloudscape.engine.api.objects.cache import CacheManager
from cloudscape.engine.api.objects.manager import ObjectsManager
from cloudscape.engine.api.core.socket import SocketResponse
from cloudscape.common.errors import JSONError, JSONException

class APIRequest(object):
    """
    APIRequest
    
    Abstraction class for parsing the Django request object.
    """
    def __init__(self, request):
        
        # Raw request / request body
        self.raw  = request
        self.body = json.loads(request.body)

class APIBase(object):
    """
    APIBase
    
    Base class in the inheritance model used by all API utilties assigned to an endpoint, and a
    handful of other class definitions. This class contains common attributes used by all API
    utilities, such as the logger, endpoint details, external utilities, request attributes, etc.
    """
    def __init__(self, name=None, endpoint=None, utils=False, acl=None):
        """
        Initialize the APIBase class.
        
        @param name:     The module name used for the logger 
        @type  name:     str
        @param endpoint: The endpoint being accessed
        @type  endpoint: str
        @param utils:    Any external utilities required by this API endpoint
        @type  utils:    list
        @param acl:      The ACL gateway generated during request initialization
        @type  acl:      ACLGateway
        @param cache:    The CacheManager class instance
        @param cache:    CacheManager
        """
        
        # Class base / configuration / internal logger
        self.class_name   = __name__ if not name else name
        self.conf         = config.parse()
        self.log_int      = logger.create(self.class_name, self.conf.server.log)

        # External utilities / utilities object / cache manager / objects manager / ACL gateway
        self.utils        = utils
        self.util         = None
        self.cache        = CacheManager()
        self.objects      = ObjectsManager()
        self.acl          = acl

        # SocketIO client / Cache Manager
        self.socket       = SocketResponse().construct()

        # Request attributes
        self.request_raw  = None     # Raw request object
        self.action       = None     # Request action
        self.data         = None     # Any request data
        self.endpoint     = endpoint # Request endpoint
     
    def _utils(self):
        """
        Construct the external utilities object. Scan each item in the utilities list retrieved
        from the endpoint database entry, and attempt to create an instance of the module/class.
        """
        if self.utils and isinstance(self.utils, list):
            util_obj = {}
            for util in self.utils:
                mod_name   = re.compile('(^.*)\.[^\.]*$').sub(r'\g<1>', util)
                class_name = re.compile('^.*\.([^\.]*$)').sub(r'\g<1>', util)
                
                # Import each enabled utility class
                mod_obj    = importlib.import_module(mod_name)
                class_obj  = getattr(mod_obj, class_name)
                class_inst = class_obj(copy.copy(self))
                self.log_int.info('Loading utility class: [%s]' % class_inst)
                
                # Add to the utilities object
                util_obj[class_name] = class_inst
            self.util = Collection(util_obj).get()
        
    def _set_action(self):
        """
        Set the API request action.
        """
        self.action = self._get_request_data('action')
        
    def _get_request_data(self, key, default=None):
        """
        Retrieve request data from the body by key.
        """
        
        # If the key is found
        if key in self.request.body:
            return self.request.body[key]
        
        # If no key is found, return the default value
        return default
        
    def _set_data(self):
        """
        Set the API request data if any is found.
        """
        self.data = self._get_request_data('_data', {})
        
    def _set_websock(self):
        """
        Check if the client is making a request via the Socket.IO proxy server.
        """
        if 'socket' in self.request.body:
            
            # Log the socket connection
            self.log_int.info('Received connection from web socket client: %s' % str(self.request.body['socket']))
            
            # Set the web socket response attributes
            self.websock = self.socket.set(self.request.body['socket'])
        else:
            self.websock = None
        
    def get_data(self, key, default=False):
        """
        Retrieve a key value from the API data object.
        """
        if key in self.data:
            return self.data[key]
        return default
        
    def get_logger(self, client):
        """
        Return an instance of the APILogger for non-endpoint classes.
        
        @param client: The IP address of the API client
        @type  client: str
        """
        self.log = APILogger(self, client)
        return self
        
    def construct(self, request):
        """
        Construct and return the request object and logger.
        
        @param request: The raw Django request object
        @type  request: 
        """
        
        # Construct the request object
        self.request = APIRequest(request)
        
        # Client address and API user
        self.client  = self.request.raw.META['REMOTE_ADDR']
        self.user    = self._get_request_data('api_user')
        self.group   = self._get_request_data('api_group')
        
        # Check if a web socket is making an API call
        self._set_websock()
        
        # Set the request data and action for non-authentication requests
        if not self.endpoint == 'auth/get':
            
            # Set API data / action
            self._set_data()
            self._set_action()
        
        # Set the logger object
        self.log = APILogger(self)
        
        # Import the utility classes
        self._utils()
        
        # Return the constructed API object, ready for authentication or other requests
        return valid(self)
    
class APILogger(APIBase):
    """
    APILogger
    
    Common logger class used to handle logging messages and returning HTTP responses.
    """
    def __init__(self, parent, client=None):
        """
        Initialize APILogger

        @param parent: Parent class attributes
        @type  parent: class
        @param client: The client IP address
        @type  client: str
        """
        super(APILogger, self).__init__()
        self.parent       = parent
        self.content_type = self._get_content_type()

        # Container for the current log message
        self.log_msg = None

        # Default parameters
        if hasattr(self.parent, 'client') and not client:
            self.client = parent.client
        else:
            self.client = 'cloudscape' if not client else client

    def _get_content_type(self):
        """
        Determine the content type for HTTP responses. Right now this returns a static string,
        but depending on the response message, can be modified to change the content type.
        """
        return 'application/json'

    def _websock_response(self, status, _data={}):
        """
        Construct and return a JSON web socket response for the Socket.IO proxy server.
        
        @param status: Boolean string
        @type  status: str
        @param data:   Any response data in addition to the body message
        @type  data:   dict
        """
        return json.dumps({
            'room':     self.parent.websock['room'],
            'msg':      self.log_msg,
            'endpoint': self.parent.endpoint,
            'callback': False if not ('callback' in self.parent.websock) else self.parent.websock['callback'],
            'status':   status,
            '_data':    _data
        }, cls=DjangoJSONEncoder)

    def _api_response(self, ok=False, _data={}):
        """
        Construct the API response body to send back to clients. Constructs the websocket data
        to be interpreted by the Socket.IO proxy server if relaying back to a web client.
        """
        
        # Status flag
        status = 'true' if ok else 'false'
        
        # Web socket responses
        if self.parent.websock:
            return self._websock_response(status, _data)
            
        # Any endpoints that don't supply web socket responses    
        else:
            
            # Return a JSON encoded object if a dictionary or list
            if isinstance(self.log_msg, dict) or isinstance(self.log_msg, list):
                return json.dumps(self.log_msg, cls=DjangoJSONEncoder)
            
            # Otherwise return a string
            return self.log_msg

    def info(self, log_msg):
        """
        Handle the logging of information messages.
        """
        self.log_msg = log_msg
        self.log_int.info('client(%s): %s' % (self.client, log_msg))
        return log_msg
        
    def debug(self, log_msg):
        """
        Handle the logging of debug messages.
        """
        self.log_int.info('client(%s): %s' % (self.client, log_msg))
        return log_msg
        
    def success(self, log_msg, web_data={}):
        """
        Handle the logging of success messages. Returns an HTTP response object that can be
        sent by the API request handler back to the client.
        """
        def _set_log_msg(log_msg):
            if not isinstance(log_msg, list) and not isinstance(log_msg, dict):
                return 'API request was successfull' if not log_msg else log_msg
            else:
                return log_msg

        # Default log message if not specified
        self.log_msg = _set_log_msg(log_msg)
            
        # Log the success message
        self.log_int.info('client(%s): %s' % (self.client, log_msg))
        
        # Return the HTTP response
        return HttpResponse(self._api_response(True, web_data), self.content_type, status=200)
    
    def exception(self, log_msg=None, code=None, web_data={}):
        """
        Handle the logging of exception messages. Returns an HTTP response object that can be
        sent by the API request handler back to the client.
        """
        
        # Default log message if not specified
        self.log_msg = 'An exception occured when processing your API request' if not log_msg else log_msg
    
        # Log the exception
        self.log_int.exception('client(%s): %s' % (self.client, self.log_msg))
    
        # If error code is specified and is an integer
        if code and isinstance(code, int):
        
            # Return the HTTP response
            return HttpResponse(self._api_response(False, web_data), self.content_type, status=code)
        else:
            return self.log_msg
    
    def error(self, log_msg=None, code=None, web_data={}):
        """
        Handle the logging of error messages. Returns an HTTP response object that can be
        sent by the API request handler back to the client.
        """
        
        # Default log message if not specified
        self.log_msg = 'An unknown error occured when processing your API request' if not log_msg else log_msg
        
        # Log the error message
        self.log_int.error('client(%s): %s' % (self.client, self.log_msg))
        
        # If error code is specified and is ant integer
        if code and isinstance(code, int):
        
            # Return the HTTP response
            return HttpResponse(self._api_response(False, web_data), self.content_type, status=code)
        else:
            return self.log_msg