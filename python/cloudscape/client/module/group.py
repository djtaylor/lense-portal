class GroupAPI:
    """
    Class wrapper for requests to the API group utilities.
    """
    def __init__(self, parent):
        self.parent = parent
        
    def get(self, data={}):
        """
        Get details for either a single or all groups.
        """
        return self.parent._get('group/get', data=data)
    
    def create(self, data={}):
        """
        Create a new group.
        """
        return self.parent._post('group/create', data=data)
    
    def delete(self, data={}):
        """
        Delete a group.
        """
        return self.parent._post('group/delete', data=data)
    
    def update(self, data={}):
        """
        Update a group.
        """
        return self.parent._post('group/update', data=data)
    
    def add_member(self, data={}):
        """
        Add a member to a group.
        """
        return self.parent._post('group/member/add', data=data)
    
    def remove_member(self, data={}):
        """
        Remove a member from the group.
        """
        return self.parent._post('group/member/remove', data=data)