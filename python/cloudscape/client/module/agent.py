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
        return self.parent._post('agent/poll', data=data)
    
    def system(self, data={}):
        """
        API method for uploading system information.
        """
        return self.parent._post('agent/system', data=data)
    
    def status(self, data={}):
        """
        API method for updating the agent run status.
        """
        return self.parent._post('agent/status', data=data)
    
    def formula(self, data={}):
        """
        API method for uploading formula run results.
        """
        return self.parent._post('agent/formula', data=data)
    
    def sync(self, data={}, params={}):
        """
        API method for retrieving synchronization data.
        """
        return self.parent._get('agent/sync', data=data, params=params)