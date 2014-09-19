class NetworkAPI:
    """
    Class wrapper for requests to network utilities.
    """
    def __init__(self, parent):
        self.parent = parent
       
    def get_router(self, data=None):
        """
        Get router details.
        """
        return self.parent._get('network/router/get', data=data)
    
    def create_router(self, data=None):
        """
        Create a new router.
        """
        return self.parent._post('network/router/create', data=data)
    
    def delete_router(self, data=None):
        """
        Delete an existing router.
        """
        return self.parent._post('network/router/delete', data=data)
    
    def update_router(self, data=None):
        """
        Update an existing router.
        """
        return self.parent._post('network/router/update', data=data)
    
    def add_router_interface(self, data=None):
        """
        Add a new interface to a router.
        """
        return self.parent._post('network/router/interface/add', data=data)
    
    def remove_router_interface(self, data=None):
        """
        Remove an interface from a router.
        """
        return self.parent._post('network/router/interface/remove', data=data)
    
    def get_ipv4_block(self, data=None):
        """
        Retrieve details for IPv4 network blocks.
        """
        return self.parent._get('network/block/ipv4/get', data=data)
    
    def create_ipv4_block(self, data=None):
        """
        Create a new IPv4 network block.
        """
        return self.parent._post('network/block/ipv4/create', data=data)
    
    def delete_ipv4_block(self, data=None):
        """
        Delete an existing IPv4 network block.
        """
        return self.parent._post('network/block/ipv4/delete', data=data)
    
    def update_ipv4_block(self, data=None):
        """
        Update an existing IPv4 network block.
        """
        return self.parent._post('network/block/ipv4/update', data=data)
    
    def get_ipv6_block(self, data=None):
        """
        Retrieve details for IPv6 network blocks.
        """
        return self.parent._get('network/block/ipv6/get', data=data)
    
    def create_ipv6_block(self, data=None):
        """
        Create a new IPv6 network block.
        """
        return self.parent._post('network/block/ipv6/create', data=data)
    
    def delete_ipv6_block(self, data=None):
        """
        Delete an existing IPv6 network block.
        """
        return self.parent._post('network/block/ipv6/delete', data=data)
    
    def update_ipv6_block(self, data=None):
        """
        Update an existing IPv6 network block.
        """
        return self.parent._post('network/block/ipv6/update', data=data)