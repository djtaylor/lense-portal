class UserAPI:
    """
    Python interface for interacting with the CloudScape users API endpoint.
    """
    def __init__(self, parent):
        self.parent = parent
        
    def get(self, data={}):
        """
        Get details for either a single or all users.
        """
        return self.parent._get(data=data, action='get', path='user')
    
    def create(self, data={}):
        """
        Create a new user account.
        """
        return self.parent._post(data=data, action='create', path='user')