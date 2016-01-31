import sys
import traceback
from threading import Thread
from collections import OrderedDict

# Django Libraries
from django.shortcuts import render
from django.template import RequestContext, Context, loader
from django.http import HttpResponseServerError

class PortalTemplate(object):
    """
    Construct the template data needed to render each page, and return the HTTP response
    and data needed to render the page client-side.
    """
    def __init__(self, portal):
        """
        Initialize the portal template class.
        """ 
     
        # URL panel
        self.panel       = LENSE.REQUEST.GET('panel')
        
        # Threaded API responses
        self._response   = {}
        
        # Template data
        self._tdata      = {}
     
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
        
        # User object
        user = LENSE.OBJECTS.USER.get(LENSE.REQUEST.USER.name)
        
        # Set the base parameters
        params = {
            'BASE': {
                     
                # Connection user attributes
                'user': {
                    'is_admin': LENSE.REQUEST.USER.admin,
                    'is_authenticated': LENSE.REQUEST.USER.authorized,
                    'groups': user.groups,
                    'name': user.username,
                    'email': user.email
                },
                     
                # API connection parameters
                'api': {
                    'params': LENSE.CLIENT.params(['user', 'group', 'key'])
                },
                     
                # Request parameters
                'request': {
                    'current': LENSE.REQUEST.current,
                    'path': LENSE.REQUEST.path       
                }
            }
        }
        
        # Replace the API URL with the Socket.IO proxy
        if params['BASE']['api']['params']:
            params['BASE']['api']['params']['url'] = '{0}://{1}:{2}'.format(LENSE.CONF.socket.proto, LENSE.CONF.socket.host, LENSE.CONF.socket.port)
        
        # Merge extra template parameters
        for k,v in objs.iteritems():
            
            # Do not overwrite the 'BASE' key
            if k == 'BASE':
                raise Exception('Template data key [BASE] is reserved for internal use only')
            
            # Append the template data key
            params[k] = v
            
        # Return the template data object
        return params
       
    def api_call(self, path, method, data=None):
        """
        Wrapper method for the APIClient class instance.
        """
        response = LENSE.CLIENT.request(path, method, data)
        
        # Return response content
        return response.content 
    
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
            return render(self.portal.request.RAW, 'interface.html', self._tdata)
        
        # Failed to render template
        except Exception as e:
            
            # Log the exception
            LENSE.LOG.exception('Failed to render application template interface: {0}'.format(str(e)))
            
            # Get the exception data
            e_type, e_info, e_trace = sys.exc_info()
                
            # Format the exception message
            e_msg = '{0}: {1}'.format(e_type.__name__, e_info)
            
            # Load the error template
            t = loader.get_template('core/error/500.html')
            
            # Return a server error
            return HttpResponseServerError(t.render(RequestContext(self.portal.request.RAW, {
                'error': 'An error occurred when rendering the requested page.',
                'debug': None if LENSE.CONF.portal.debug else (e_msg, reversed(traceback.extract_tb(e_trace)))
            })))