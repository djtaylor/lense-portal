class ClusterAPI:
    def __init__(self, parent):
        self.parent = parent
    
    def search(self, data=None):
        """
        Search the cluster index.
        """
        return self.parent._get('cluster/search', data=data)
    
    def index(self, data=None):
        """
        Rebuild the cluster index.
        """
        return self.parent._post('cluster/index', data=data)
        
    def stats(self, data=None):
        """
        Retrieve statistics for cluster hosts.
        """
        return self.parent._get('cluster/stats', data=data)