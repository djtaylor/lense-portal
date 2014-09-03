import json
import requests

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.client.base import APIBase
from cloudscape.common.utils import parse_response

class APIConnect:
    """
    Factory class used to construct an API connection object using the APIBase class. If supplying
    an API key, a token will be retrieved then passed off to the APIBase class.
    """
    def __init__(self, user=None, group=None, api_key=None, api_token=None):
        
        # API connection attributes
        self.api_user  = user       # API user
        self.api_group = group      # API group
        self.api_key   = api_key    # API key
        self.api_token = api_token  # API token
        
        # Configuration
        self.conf      = config.parse()

        # Server URL
        self.api_url   = '%s://%s:%s' % (self.conf.server.proto, self.conf.server.host, self.conf.server.port)

    def construct(self):
        """
        Construct and return the API connection and parameters objects.
        """
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
                'url':   self.api_url
            }
                
            # Return the API client
            return APIBase(
                user  = self.api_user, 
                group = self.api_group,
                token = self.api_token, 
                url   = self.api_url
            ), self.params
        
