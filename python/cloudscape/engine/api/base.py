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
from cloudscape.common.http import PATH, MIME_TYPE
from cloudscape.common.utils import valid, invalid
from cloudscape.common.collection import Collection
from cloudscape.engine.api.objects.cache import CacheManager
from cloudscape.engine.api.objects.manager import ObjectsManager
from cloudscape.engine.api.core.socket import SocketResponse
from cloudscape.common.errors import JSONError, JSONException

class APIBase(object):
    """
    APIBase
    
    Base class in the inheritance model used by all API utilties assigned to a path, and a
    handful of other class definitions. This class contains common attributes used by all API
    utilities, such as the logger, path details, external utilities, request attributes, etc.
    """
    def __init__(self, request=None, utils=False, acl=None):
        """
        Initialize the APIBase class.
        
        @param name:     The module name used for the logger 
        @type  name:     str
        @param request:  The request object from RequestManager
        @type  request:  RequestObject
        @param utils:    Any external utilities required by this API endpoint
        @type  utils:    list
        @param acl:      The ACL gateway generated during request initialization
        @type  acl:      ACLGateway
        @param cache:    The CacheManager class instance
        @param cache:    CacheManager
        """
        
        # Request object / data / path
        self.request      = request
        self.data         = request.data
        self.path         = request.path
        
        # Configuration / internal logger
        self.conf         = config.parse()
        self.log_int      = logger.create(self.path, self.conf.server.log)

        # External utilities / utilities object / cache manager / objects manager / ACL gateway
        self.utils        = utils
        self.util         = None
        self.cache        = CacheManager()
        self.objects      = ObjectsManager()
        self.acl          = acl

        # SocketIO client / web socket object
        self.socket       = SocketResponse().construct()
        self.websock      = None
     
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
        
    def _set_websock(self):
        """
        Check if the client is making a request via the Socket.IO proxy server.
        """
        if 'socket' in self.request.data:
            
            # Log the socket connection
            self.log_int.info('Received connection from web socket client: %s' % str(self.request.data['socket']))
            
            # Set the web socket response attributes
            self.websock = self.socket.set(self.request.data['socket'])
        else:
            self.websock = None
        
    def get_logger(self, client):
        """
        Return an instance of the APILogger for non-endpoint classes.
        
        @param client: The IP address of the API client
        @type  client: str
        """
        self.log = APILogger(self, client)
        return self
        
    def construct(self):
        """
        Construct and return the APIBase class.
        """
        
        # Check if a web socket is making an API call
        self._set_websock()
        
        # Import the utility classes
        self._utils()
        
        # Set the logger object
        self.log = APILogger(self)
        
        # Return the constructed API object, ready for authentication or other requests
        return valid(self)
    
class APILogger(object):
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
        self.api     = parent

        # Container for the current log message
        self.log_msg = None

        # Default parameters
        if hasattr(self.api.request, 'client') and not client:
            self.client = self.api.request.client
        else:
            self.client = 'localhost' if not client else client

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

    def _api_response(self, ok=False, data={}):
        """
        Construct the API response body to send back to clients. Constructs the websocket data
        to be interpreted by the Socket.IO proxy server if relaying back to a web client.
        """
        
        # Status flag
        status = 'true' if ok else 'false'
        
        # Web socket responses
        if self.api.websock:
            return self._websock_response(status, data)
            
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
        return HttpResponse(self._api_response(True, web_data), MIME_TYPE.APPLICATION.JSON, status=200)
    
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
            return HttpResponse(self._api_response(False, web_data), MIME_TYPE.APPLICATION.JSON, status=code)
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
            return HttpResponse(self._api_response(False, web_data), MIME_TYPE.APPLICATION.JSON, status=code)
        else:
            return self.log_msg