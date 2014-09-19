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
    
    def get_endpoints(self, data=None):
        """
        Retrieve a listing of API endpoints.
        """
        return self.parent._get('auth/endpoints/get', data=data)
    
    def open_endpoint(self, data=None):
        """
        Open an endpoint for editing.
        """
        return self.parent._get('auth/endpoints/open', data=data)
    
    def close_endpoint(self, data=None):
        """
        Check in an endpoint and release the editing lock.
        """
        return self.parent._get('auth/endpoints/close', data=data)
    
    def validate_endpoint(self, data=None):
        """
        Validate changes to an endpoint prior to saving.
        """
        return self.parent._post('auth/endpoints/validate', data=data)
    
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