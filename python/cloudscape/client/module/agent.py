class AgentAPI:
    """
    API module for handling access to the host agent endpoints.
    """
    def __init__(self, parent):
        self.parent = parent

    def poll(self, data={}):
        """
        API method for uploading polling data.
        """
        return self.parent._post(data=data, action='poll', path='agent')
    
    def system(self, data={}):
        """
        API method for uploading system information.
        """
        return self.parent._post(data=data, action='system', path='agent')
    
    def status(self, data={}):
        """
        API method for updating the agent run status.
        """
        return self.parent._post(data=data, action='status', path='agent')
    
    def formula(self, data={}):
        """
        API method for uploading formula run results.
        """
        return self.parent._post(data=data, action='formula', path='agent')
    
    def sync(self, data={}):
        """
        API method for retrieving synchronization data.
        """
        return self.parent._get(data=data, action='sync', path='agent')