class AuthAPI:
    """
    Class wrapper for authorization utilities.
    """
    def __init__(self, parent):
        self.parent = parent
    
    def get_token(self, data=None):
        """
        Get an API token.
        """
        return self.parent._get('auth/get', data=data)
    
    def get_acl(self, data=None):
        """
        Get an object containing ACL definitions.
        """
        return self.parent._get('auth/acl/get', data=data)
    
    def update_acl(self, data=None):
        """
        Update an existing ACL definition.
        """
        return self.parent._post('auth/acl/update', data=data)
    
    def get_utilities(self, data=None):
        """
        Retrieve a listing of API utilities.
        """
        return self.parent._get('auth/utilities/get', data=data)
    
    def open_utility(self, data=None):
        """
        Open a utility for editing.
        """
        return self.parent._get('auth/utilities/open', data=data)
    
    def close_utility(self, data=None):
        """
        Check in a utility and release the editing lock.
        """
        return self.parent._get('auth/utilities/close', data=data)
    
    def validate_utility(self, data=None):
        """
        Validate changes to a utility prior to saving.
        """
        return self.parent._post('auth/utilities/validate', data=data)
    
    def create_acl_object(self, data=None):
        """
        Create a new ACL object.
        """
        return self.parent._post('auth/acl/objects/create', data=data)
    
    def get_acl_objects(self, data=None):
        """
        Retrieve a listing of ACL object types.
        """
        return self.parent._get('auth/acl/objects/get', data=data)
    
    def delete_acl_objects(self, data=None):
        """
        Delete an ACL object definition.
        """
        return self.parent._post('auth/acl/objects/delete', data=data)