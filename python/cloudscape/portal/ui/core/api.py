from cloudscape.client.manager import APIConnect
from cloudscape.engine.api.app.user.models import DBUser, DBUserAPIKeys

class APIClient:
    """
    Wrapper class use to create an instance of the API client to be used when retrieving
    API data for rendering in a page template.
    """
    
    def get(self, user=None, group=None):
        """
        Get and return the API client object.
        """
        
        # No user defined or not user logged in
        if not user or not group:
            return False
        
        # Get the user object
        user_obj = DBUser.objects.get(username=user)
        
        # Query the API key for the logged in user
        api_key_row = DBUserAPIKeys.objects.filter(user=user_obj.uuid).values('api_key')
        if not api_key_row:
            return False
        
        # Get the API key for the logged in user
        api_key = api_key_row[0]['api_key']
        if not api_key:
            return False
        
        # Return the API client object
        return APIConnect(
            api_user  = user, 
            api_group = group,
            api_key   = api_key
        ).construct()