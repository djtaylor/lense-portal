import sys
import json
import traceback

# Django Libraries
from django.http import HttpResponse

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger

# Configuration / Logger
CONF = config.parse()
LOG  = logger.create(__name__, CONF.server.log)

# Error codes to message mappings
ERR_MESSAGE = {
    500: 'An internal server error occurred, please contact your administrator',
    400: 'An error occurred while validating the request',
    401: 'An error occured while authorizing the request'
}

class JSONErrorBase(object):
    """
    Base response class for error and exception responses.
    """
    def __init__(self, error=None, code=500, exception=False):

        # Construct the JSON error object
        self.error_object = {
            'message': ERR_MESSAGE.get(code, 'An unknown error has occurred, please contact your administrator'),
            'code':    code,
            'error':   error
        }
        
        # If an error message is provided
        if error:
            LOG.error(error)
        
        # If providing a stack trace for debugging and debugging is enabled
        if exception and CONF.server.debug:
            self.error_object.update({
                'debug': self._extract_trace()
            })
    
    def _extract_trace(self):
        """
        Extract traceback details from an exception.
        """
        
        # Get the exception data
        try:
            e_type, e_info, e_trace = sys.exc_info()
        
            # Exception message
            e_msg = '%s: %s' % (e_type.__name__, e_info)
        
            # Log the exception
            LOG.exception(e_msg)
        
            # Return the exception message and traceback
            return {
                'exception': e_msg,
                'traceback': traceback.extract_tb(e_trace)
            }
            
        # Failed to extract exception data
        except:
            return None
        
    def response(self):
        """
        Construct and return the response object.
        """
        return HttpResponse(json.dumps(self.error_object), content_type='application/json', status=code)

class JSONError(JSONErrorBase):
    """
    Client error response object.
    """
    def __init__(self, error=None, code=400):
        super(JSONError, self).__init__(error=error, code=code)
    
class JSONException(JSONErrorBase):
    """
    Internal server error response object.
    """
    def __init__(self):
        super(JSONException, self).__init__(exception=True)
    
    
        
    