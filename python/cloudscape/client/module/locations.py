class LocationsAPI:
    def __init__(self, parent):
        self.parent = parent
       
    def get_datacenters(self, data=None):
        return self.parent._get(data=data, action='get', path='locations/datacenters')
    
    def update_datacenters(self, data={}):
        return self.parent._post(data=data, action='update', path='locations/datacenters')
    
    def create_datacenters(self, data={}):
        return self.parent._post(data=data, action='create', path='locations/datacenters')
    
    def delete_datacenters(self, data={}):
        return self.parent._post(data=data, action='delete', path='locations/datacenters')