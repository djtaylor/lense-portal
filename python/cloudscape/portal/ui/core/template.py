import re
import sys
import json
import base64
import traceback
from threading import Thread
from collections import OrderedDict

# Django Libraries
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponseServerError

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.portal.ui.core import utils
from cloudscape.portal.ui.core.filter import APIFilter
from cloudscape.engine.api.app.user.models import DBUserDetails

class PortalTemplate(object):
    """
    Construct the template data needed to render each page, and return the HTTP response
    and data needed to render the page client-side.
    """
    
    def __init__(self, portal):
        """
        Initialize the portal template class.
        """
        self.portal = portal
        
        # Shared modules
        self.json        = json
        self.base64      = base64
        self.OrderedDict = OrderedDict  
        
        # Configuration / logger
        self.conf        = config.parse()
        self.log         = logger.create(__name__, self.conf.portal.log)
     
        # URL panel
        self.panel       = self.get_query_key('panel')
        
        # Threaded API responses
        self._response   = {}
        
        # Template data
        self._tdata      = {}
     
        # Response filter
        self.filter      = APIFilter()
     
    def redirect(self, location):
        """
        Return an HTTPResponseRedirect object.
        """
        return HTTPResponseRedirect(location)
     
    def get_query_key(self, key):
        """
        Retrieve a key value from the URL query string.
        """
        
        # Split the query string into an array of key/value pairs
        query_obj = {}
        for query_pair in self.portal.request.query.split('&'):
            if '=' in query_pair:
                query_set = query_pair.split('=')
                query_obj[query_set[0]] = query_set[1]
            else:
                query_obj[query_pair] = True
        
        # If the key is found
        if key in query_obj:
            return query_obj[key]
        
        # Key not found
        return False
     
    def request_contains(self, req=None, attr=None, values=None):
        """
        Check if the request data contains the specified attribute and values combination.
        """
        if not req or not attr:
            return False
     
        # Check if the request data object contains the specified attribute
        if hasattr(req, attr):
            
            # If testing for supported attributed values
            if values and isinstance(values, list):
                if getattr(req, attr) in values:
                    return True
                return False
            return True
        return False
       
    def set_template(self, data={}):
        """
        Set the target template file and data.
        """
        self._tdata = self._template_data(data)
       
    def set_redirect(self, path):
        """
        Return a template data redirect attribute.
        """
        return { 'redirect': path }
       
    def _template_data(self, objs={}):
        """
        Merge base template data and page specific template data. 
        """
        
        # Set the base parameters
        base = {
            'api_params':    None if not hasattr(self.portal.api, 'params') else self.portal.api.params,
            'authenticated': self.portal.authenticated,
            'request': {
                'current': self.portal.request.current
            }
        }
        
        # Replace the API URL with the Socket.IO proxy
        if base['api_params']:
            base['api_params']['url'] = '%s://%s:%s' % (self.conf.socket.proto, self.conf.socket.host, self.conf.socket.port)
        
        # Merge extra template parameters
        for k,v in objs.iteritems():
            base[k] = v
            
        # Return the template data object
        return base
       
    def api_call(self, base, method, data=None):
        """
        Wrapper method for the APIClient class instance.
        """
        
        # Make sure the base attribute exists
        if hasattr(self.portal.api.client, base):
            api_base = getattr(self.portal.api.client, base)
            
            # Make sure the method attribute exists
            if hasattr(api_base, method):
                api_method = getattr(api_base, method)
       
                # Run the API request and return a filtered response
                return self.filter.object(self.portal.api.response(api_method(data))).map('%s.%s' % (base, method))
       
        # Invalid base/method attribute
        return False    
    
    def _api_call_threaded_worker(self, key, base, method, data=None):
        """
        Worker method for handled threaded API calls.
        """
        self._response[key] = self.api_call(base, method, data)
    
    def api_call_threaded(self, requests):
        """
        Interface for a multi-threaded API call, to speed up the request/response cycle when
        calling multiple endpoints when rendering a template.
        """
        
        # Threads / responses
        threads   = []
        
        # Process each request
        for key,attr in requests.iteritems():
        
            # Get any request data
            data   = None if (len(attr) == 2) else attr[2]
        
            # Create the thread, append, and start
            thread = Thread(target=self._api_call_threaded_worker, args=[key, attr[0], attr[1], data])
            threads.append(thread)
            thread.start()
            
        # Wait for the API calls to complete
        for thread in threads:
            thread.join()
            
        # Return the response object
        return self._response
        
    def response(self):
        """
        Construct and return the template response.
        """
        
        # If redirecting
        if 'redirect' in self._tdata:
            return HttpResponseRedirect(self._tdata['redirect'])
        
        # Return the template response
        try:
            return render_to_response('interface.html', self._tdata, context_instance=RequestContext(self.portal.request.RAW))
        
        # Failed to render template
        except Exception as e:
            
            # Log the exception
            self.log.exception('Failed to render application template interface: %s' % str(e))
            
            # Get the exception data
            e_type, e_info, e_trace = sys.exc_info()
                
            # Format the exception message
            e_msg = '%s: %s' % (e_type.__name__, e_info)
            
            # Load the error template
            t = loader.get_template('core/error/500.html')
            
            # Return a server error
            return HttpResponseServerError(t.render(RequestContext(self.portal.request.RAW, {
                'error': 'An error occurred when rendering the requested page.',
                'debug': None if self.conf.portal.debug else (e_msg, reversed(traceback.extract_tb(e_trace)))
            })))