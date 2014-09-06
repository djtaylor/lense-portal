class NetworkAPI:
    def __init__(self, parent):
        self.parent = parent
       
    def get_router(self, data=None):
        return self.parent._get(data=data, action='get', path='network/router')
    
    def create_router(self, data=None):
        return self.parent._post(data=data, action='create', path='network/router')
    
    def delete_router(self, data=None):
        return self.parent._post(data=data, action='delete', path='network/router')
    
    def update_router(self, data=None):
        return self.parent._post(data=data, action='update', path='network/router')