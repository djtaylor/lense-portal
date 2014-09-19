class VCloudAPI:
    """
    Class wrapper for requests to the VCloud proxy utilities.
    """
    def __init__(self, parent):
        self.parent = parent
        
    def cache(self, data=None):
        """
        Cache VCloud API data.
        """
        return self.parent._post('vcloud/cache', data=data)