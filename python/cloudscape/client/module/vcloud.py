"""
VCloud API Module
"""
class VCloudAPI:
    def __init__(self, parent):
        self.parent = parent
        
    """
    Cache VCloud API Data
    """
    def cache(self, data=None):
        return self.parent._post(data=data, action='cache', path='vcloud')