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
    
    def add_router_interface(self, data=None):
        return self.parent._post(data=data, action='add', path='network/router/interface')
    
    def remove_router_interface(self, data=None):
        return self.parent._post(data=data, action='remove', path='network/router/interface')
    
    def get_ipv4_block(self, data=None):
        return self.parent._get(data=data, action='get', path='network/block/ipv4')
    
    def create_ipv4_block(self, data=None):
        return self.parent._post(data=data, action='create', path='network/block/ipv4')
    
    def delete_ipv4_block(self, data=None):
        return self.parent._post(data=data, action='delete', path='network/block/ipv4')
    
    def update_ipv4_block(self, data=None):
        return self.parent._post(data=data, action='update', path='network/block/ipv4')
    
    def get_ipv6_block(self, data=None):
        return self.parent._get(data=data, action='get', path='network/block/ipv6')
    
    def create_ipv6_block(self, data=None):
        return self.parent._post(data=data, action='create', path='network/block/ipv6')
    
    def delete_ipv6_block(self, data=None):
        return self.parent._post(data=data, action='delete', path='network/block/ipv6')
    
    def update_ipv6_block(self, data=None):
        return self.parent._post(data=data, action='update', path='network/block/ipv6')