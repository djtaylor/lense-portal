import datetime

# Django Libraries
from django.conf import settings

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.utils import valid, invalid, rstring
from cloudscape.engine.api.app.user.models import DBUserAPITokens, DBUser
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostAPITokens

class APIToken(object):
    """
    API class used to assist in validating, creating, and retrieving API authentication tokens.
    """
    def __init__(self):
        
        # Configuration / logger objects
        self.conf = config.parse()
        self.log  = logger.create(__name__, self.conf.server.log)
    
    def _get_api_token(self, id):
        """
        Retrieve the API token for a user or host account.
        """
        
        # Check if a user or host
        api_user = DBUser.objects.filter(username=id).count()
        api_host = DBHostDetails.objects.filter(uuid=id).count()

        # If not an existing host or user
        if not api_user and not api_host:
            return invalid('Authentication failed, account [%s] not found in the database' % id)
        
        # If for some reason both a user and host
        if api_user and api_host:
            return invalid('Authentication failed, account [%s] is both user and host' % id)

        # Retrieve API token for a user account
        if api_user:
            
            # Make sure the user is enabled
            user_obj = DBUser.objects.get(username=id)
            if not user_obj.is_active:
                return invalid('Authentication failed, account [%s] is disabled' % id)
            
            # Return the API token row
            api_token_row = list(DBUserAPITokens.objects.filter(user=user_obj.uuid).values())
            
        # Retrieve API token for a host account
        if api_host:
            api_token_row = list(DBHostAPITokens.objects.filter(host=id).values())

        # User or host has no API key
        if not api_token_row:
            return valid(None)
        return valid(api_token_row[0]['token'])
    
    def create(self, type=None, id=None):
        """
        Generate a new API authentication token.
        """
        token_str = rstring(255)
        expires   = datetime.datetime.now() + datetime.timedelta(hours=settings.API_TOKEN_LIFE)
            
        # Create a new API token
        self.log.info('Generating API token for client [%s] of type [%s]' % (id, type))
        
        # Host API token
        if type == 'host':
            db_token  = DBHostAPITokens(id = None, host=DBHostDetails.objects.get(uuid=id), token=token_str, expires=expires)
            db_token.save()
            return token_str
        
        # User API token
        elif type == 'user':
            db_token  = DBUserAPITokens(id = None, user=DBUser.objects.get(username=id), token=token_str, expires=expires)
            db_token.save()
            return token_str
        
        # Invalid account type
        else:
            self.log.error('Failed to generate token for client [%s]' % id)
            return False
    
    def get(self, id):
        """
        Get the API authentication token for a user or host account.
        """
        self.log.info('Retrieving API token for ID [%s]' % id)
            
        # Check if a user or host
        api_user  = DBUser.objects.filter(username=id).count()
        api_host  = DBHostDetails.objects.filter(uuid=id).count()
        
        # Attempt to retrieve an existing token
        api_token = self._get_api_token(id=id)
        
        # If there was an error
        if not api_token['valid']:
            return api_token
        
        # If the user doesn't have a token yet
        if api_token['content'] == None:
            if api_user:
                api_token['content'] = self.create(id=id, type='user')
            if api_host:
                api_token['content'] = self.create(id=id, type='host')
        self.log.info('Retrieved token for API ID [%s]: %s' % (id, api_token['content']))
        return api_token['content']
    
    def validate(self, request):
        """
        Validate the API token in a request from either a user or host account.
        """
        
        # Missing API user and/or API token
        if not hasattr(request, 'api_user') or not hasattr(request, 'api_token'):
            self.log.error('Missing required token validation headers [api_user] and/or [api_token]')
            return False
        self.log.info('Validating API token for ID [%s]: %s' % (request.user, request.token))
            
        # Get the users API token from the database
        db_token = self._get_api_token(id=request.user)

        # If no API token exists yet
        if not db_token['valid']:
            self.log.error(db_token['content'])
            return False

        # Make sure the token is valid
        if request.token != db_token['content']:
            self.log.error('Client [%s] has submitted an invalid API token' % request.user)
            return False
        return True