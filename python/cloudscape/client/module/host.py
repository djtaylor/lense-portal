class HostAPI:
    """
    Class wrapper for requests to host utilities.
    """
    def __init__(self, parent):
        self.parent = parent

    def add(self, data=None):
        """
        Add a new managed host.
        """
        return self.parent._post('host/add', data=data)
        
    def delete(self, data=None):
        """
        Remove a managed host an optionally the agent software.
        """
        return self.parent._post('host/delete', data=data)
        
    def update(self, data=None):
        """
        Update attributes for a single host.
        """
        return self.parent._post('host/update', data=data)
        
    def get(self, data=None):
        """
        Retrieve details for a single or all hosts.
        """
        return self.parent._get('host/get', data=data)
    
    def stats(self, data=None):
        """
        Retrieve polling statistics for a managed host.
        """
        return self.parent._get('host/stats', data=data)
    
    def get_formula(self, data=None):
        """
        Retrieve formula details for a managed host.
        """
        return self.parent._get('host/get', data=data)
    
    def remove_formula(self, data=None):
        """
        Remove/uninstall a formula from a managed host.
        """
        return self.parent._post('host/formula/remove', data=data)
    
    def control_agent(self, data=None):
        """
        Control agent software on a host.
        """
        return self.parent._post('host/agent/control', data=data)
    
    def update_agent(self, data=None):
        """
        Update agent software on a host.
        """
        return self.parent._post('host/agent/update', data=data)
    
    def get_group(self, data=None):
        """
        Retrieve a single or all host groups.
        """
        return self.parent._get('host/group/get', data=data)
    
    def get_service(self, data=None):
        """
        Retrieve either a single or all services for a managed host.
        """
        return self.parent._get('host/service/get', data=data)
    
    def set_service(self, data=None):
        """
        Change the target state for a host service.
        """
        return self.parent._post('host/service/set', data=data)
    
    def get_dkey(self, data=None):
        """
        Get deployment keys for Windows servers.
        """
        return self.parent._get('host/dkey/get', data=data)
    
    def update_dkey(self, data=None):
        """
        Update an existing Windows deployment key.
        """
        return self.parent._post('host/dkey/update', data=data)
    
    def set_dkey(self, data=None):
        """
        Set a new default Windows deployment key.
        """
        return self.parent._post('host/dkey/set', data=data)