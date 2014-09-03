import sys
import json
import requests
import importlib

# CloudScape Libraries
from cloudscape.common.vars import C_CLIENT
from cloudscape.common.utils import parse_response

class APIBase:
    """
    The base class inherited by API path specific classes. This class provides access to
    command methods to GET and POST data to the API server.
    """
    def __init__(self, user=None, group=None, token=None, url=None):
        self._user    = user
        self._group   = group
        self._token   = token
        self._url     = url
        self._headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        # Construct the API map
        self._construct_map()

    def _construct_map(self):
        """
        Method to construct the API request objects.
        """

        # Load the mapper JSON manifest
        map_json = None
        with open('%s/mapper.json' % C_CLIENT, 'r') as f:
            map_json = json.loads(f.read())

        # Set the modules base
        mod_base = map_json['base']
        
        # Load each module
        for mod in map_json['modules']:
            api_mod = '%s.%s' % (mod_base, mod['module'])
            
            # Load the API endpoint handler
            ep_mod   = importlib.import_module(api_mod)
            ep_class = getattr(ep_mod, mod['class'])
            ep_inst  = ep_class(self)
            
            # Set the internal attribute
            setattr(self, mod['id'], ep_inst)

    def _construct_data(self, action, data=None):
        """
        Method to construct the request body JSON object, which includes the API user and
        token, the API action type, and the action data to act upon.
        """
        req_data = { 'api_user':  self._user,
                     'api_token': self._token,
                     'api_group': self._group,
                     'action':    action }
        if data:
            req_data['_data'] = data
        return req_data

    def _get(self, data=None, action=None, path=None):
        """
        Wrapper method to make GET requests to the specific API endpoint. This method will
        merge authentication data into the JSON request body.
        """
        
        # Merge in authentication data
        data_merged = self._construct_data(action, data)
        
        # Set the request URL to the API endpoint path
        get_url = '%s/%s' % (self._url, path)
        
        # POST the request and return the response
        return parse_response(requests.get(get_url, data=json.dumps(data_merged), headers=self._headers))

    def _post(self, data=None, action=None, path=None):
        """
        Wrapper method to make POST requests to the specific API endpoint. This method will
        merge authentication data into the JSON request body.
        """
        
        # Set the request URL to the API endpoint path
        post_url = '%s/%s' % (self._url, path)
        
        # Merge in authentication data
        data_merged = self._construct_data(action, data)
        
        # POST the request and return the response
        return parse_response(requests.post(post_url, data=json.dumps(data_merged), headers=self._headers))