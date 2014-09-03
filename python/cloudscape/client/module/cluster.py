class ClusterAPI:
    def __init__(self, parent):
        self.parent = parent
    
    def search(self, data={}):
        """
        Search the cluster index.
        """
        return self.parent._get(data=data, action='search', path='cluster')
    
    def index(self, data=None):
        """
        Rebuild the cluster index.
        """
        return self.parent._post(data=None, action='index', path='cluster')
        
    def stats(self, data={}):
        """
        Retrieve statistics for cluster hosts.
        """
        return self.parent._get(data=data, action='stats', path='cluster')