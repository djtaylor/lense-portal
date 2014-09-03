class GroupAPI:
    """
    Python interface for interacting with the CloudScape groups API endpoint.
    """
    def __init__(self, parent):
        self.parent = parent
        
    def get(self, data={}):
        """
        Get details for either a single or all groups.
        """
        return self.parent._get(data=data, action='get', path='group')
    
    def create(self, data={}):
        """
        Create a new group.
        """
        return self.parent._post(data=data, action='create', path='group')
    
    def delete(self, data={}):
        """
        Delete a group.
        """
        return self.parent._post(data=data, action='delete', path='group')
    
    def update(self, data={}):
        """
        Update a group.
        """
        return self.parent._post(data=data, action='update', path='group')
    
    def add_member(self, data={}):
        """
        Add a member to a group.
        """
        return self.parent._post(data=data, action='add', path='group/member')
    
    def remove_member(self, data={}):
        """
        Remove a member from the group.
        """
        return self.parent._post(data=data, action='remove', path='group/member')