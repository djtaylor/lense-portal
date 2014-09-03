class AuthAPI:
    """
    Class wrapper for the authorization endpoint.
    """
    def __init__(self, parent):
        self.parent = parent
       
    def sync_acl(self):
        """
        Sync the database ACL definitions with the endpoint templates.
        """
        return self.parent._post(data=None, action='sync', path='auth/acl')
    
    def get_acl(self,data=None):
        """
        Get an object containing ACL definitions.
        """
        return self.parent._get(data=data, action='get', path='auth/acl')
    
    def update_acl(self,data=None):
        """
        Update an existing ACL definition.
        """
        return self.parent._post(data=data, action='update', path='auth/acl')
    
    def sync_endpoints(self,data=None):
        """
        Synchronize API endpoint definitions with the database.
        """
        return self.parent._post(data=data, action='sync', path='auth/endpoints')
    
    def get_endpoints(self, data=None):
        """
        Retrieve a listing of API endpoints.
        """
        return self.parent._get(data=data, action='get', path='auth/endpoints')
    
    def open_endpoint(self, data=None):
        """
        Open an endpoint for editing.
        """
        return self.parent._get(data=data, action='open', path='auth/endpoints')
    
    def close_endpoint(self, data=None):
        """
        Check in an endpoint and release the editing lock.
        """
        return self.parent._get(data=data, action='close', path='auth/endpoints')
    
    def validate_endpoint(self, data=None):
        """
        Validate changes to an endpoint prior to saving.
        """
        return self.parent._post(data=data, action='validate', path='auth/endpoints')
    
    def create_acl_object(self, data=None):
        """
        Create a new ACL object.
        """
        return self.parent._post(data=data, action='create', path='auth/acl/objects')
    
    def get_acl_objects(self, data=None):
        """
        Retrieve a listing of ACL object types.
        """
        return self.parent._get(data=data, action='get', path='auth/acl/objects')
    
    def delete_acl_objects(self, data=None):
        """
        Delete an ACL object definition.
        """
        return self.parent._post(data=data, action='delete', path='auth/acl/objects')