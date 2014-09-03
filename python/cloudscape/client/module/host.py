class HostAPI:
    """
    API module responsible for handling host actions.
    """
    def __init__(self, parent):
        self.parent = parent
        
    def run(self, data={}):
        """
        Deprecated API method used to run an arbitrary command on a host.
        """
        return self.parent._post(data=data, action='run', path='host')

    def add(self, data={}):
        """
        Add a new managed host.
        """
        return self.parent._post(data=data, action='add', path='host')
        
    def delete(self, data={}):
        """
        Remove a managed host an optionally the agent software.
        """
        return self.parent._post(data=data, action='delete', path='host')
        
    def update(self, data={}):
        """
        Update attributes for a single host.
        """
        return self.parent._post(data=data, action='update', path='host')
        
    def get(self, data=None):
        """
        Retrieve details for a single or all hosts.
        """
        return self.parent._get(data=data, action='get', path='host')
    
    def stats(self, data={}):
        """
        Retrieve polling statistics for a managed host.
        """
        return self.parent._get(data=data, action='stats', path='host')
    
    def get_formula(self, data=None):
        """
        Retrieve formula details for a managed host.
        """
        return self.parent._get(data=data, action='get', path='host/formula')
    
    def remove_formula(self, data={}):
        """
        Remove/uninstall a formula from a managed host.
        """
        return self.parent._post(data=data, action='remove', path='host/formula')
    
    def control_agent(self, data={}):
        """
        Control agent software on a host.
        """
        return self.parent._post(data=data, action='control', path='host/agent')
    
    def update_agent(self, data={}):
        """
        Update agent software on a host.
        """
        return self.parent._post(data=data, action='update', path='host/agent')
    
    def get_group(self, data=None):
        """
        Retrieve a single or all host groups.
        """
        return self.parent._get(data=data, action='get', path='host/group')
    
    def get_service(self, data={}):
        """
        Retrieve either a single or all services for a managed host.
        """
        return self.parent._get(data=data, action='get', path='host/service')
    
    def set_service(self, data={}):
        """
        Change the target state for a host service.
        """
        return self.parent._post(data=data, action='set', path='host/service')
    
    def get_dkey(self, data=None):
        """
        Get deployment keys for Windows servers.
        """
        return self.parent._get(data=data, action='get', path='host/dkey')
    
    def update_dkey(self, data={}):
        """
        Update an existing Windows deployment key.
        """
        return self.parent._post(data=data, action='update', path='host/dkey')
    
    def set_dkey(self, data={}):
        """
        Set a new default Windows deployment key.
        """
        return self.parent._post(data=data, action='set', path='host/dkey')