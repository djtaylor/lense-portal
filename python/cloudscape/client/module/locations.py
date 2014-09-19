class LocationsAPI:
    """
    Class wrapper for requests to the location utilities.
    """
    def __init__(self, parent):
        self.parent = parent
       
    def get_datacenter(self, data=None):
        """
        Get datacenter details.
        """
        return self.parent._get('locations/datacenters/get', data=data)
    
    def update_datacenter(self, data=None):
        """
        Update an existing datacenter.
        """
        return self.parent._post('locations/datacenters/update', data=data)
    
    def create_datacenter(self, data=None):
        """
        Create a new datacenter.
        """
        return self.parent._post('locations/datacenters/create', data=data)
    
    def delete_datacenter(self, data=None):
        """
        Delete an existing datacenter.
        """
        return self.parent._post('locations/datacenters/delete', data=data)