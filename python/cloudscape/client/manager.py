import json
import requests

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.client.base import APIBase
from cloudscape.common.utils import parse_response

"""
API Client Factory Class

Takes the API user, key, and optional connection parameters. Attempts to retrieve an API
token and then returns an instance of the APIClient class for use in accessing authenticated
API calls.
"""
class APIConnect:
    def __init__(self, user=None, group=None, api_key=None, api_token=None):
        self.api_user  = user       # API user
        self.api_group = group      # API group
        self.api_key   = api_key    # API key
        self.api_token = api_token  # API token
        
        # Configuration
        self.conf      = config.parse()

    # Construct and return the API connection
    def construct(self):
        if not self.api_user or not self.api_group or not self.api_key:
            if not self.api_token:
                raise Exception('Must supply an API user/group, key, and/or token')
        else:
            
            # If the token is not defined yet
            if not self.api_token:
            
                # Authentication URL
                auth_url   = '%s/auth' % (self.conf.server.url)
                
                # Request headers
                headers    = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        
                # Define the token request data
                token_data = {
                    'api_user':  self.api_user,
                    'api_group': self.api_group,
                    'api_key':   self.api_key,
                    'action':    'get'
                }
        
                # Get an API token
                token_rsp  = parse_response(requests.get(auth_url, data=json.dumps(token_data), headers=headers))
 
            # If retrieving the token and the auth response looks OK
            if not self.api_token and token_rsp['code'] == 200:
                auth_obj       = json.loads(token_rsp['body'])
                self.api_token = auth_obj['token']
            else:
                return False, {'code': token_rsp['code'], 'body': token_rsp['body']}
                
            # API connector parameters
            self.params = {
                'user':  self.api_user,
                'group': self.api_group,
                'token': self.api_token,
                'url':   self.conf.server.url
            }
                
            # Return the API client
            return APIBase(
                user  = self.api_user, 
                group = self.api_group,
                token = self.api_token, 
                url   = self.conf.server.url
            ), self.params
        
