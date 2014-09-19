class FormulaAPI:
    """
    Class wrapper for requests to formula utilities.
    """
    def __init__(self, parent):
        self.parent = parent

    def get(self, data=None):
        """
        Retrieve formula details.
        """
        return self.parent._get('formula/get', data=data)
    
    def verify(self, data=None):
        """
        Formula formula contents.
        """
        return self.parent._get('formula/verify', data=data)

    def create(self, data=None):
        """
        Create a new formula.
        """
        return self.parent._post('formula/create', data=data)
    
    def delete(self, data=None):
        """
        Delete an existing formula.
        """
        return self.parent._post('formula/delete', data=data)
    
    def run_service(self, data=None):
        """
        Run a service formula.
        """
        return self.parent._post('formula/run/service', data=data)
    
    def run_utility(self, data=None):
        """
        Run a utility formula.
        """
        return self.parent._post('formula/run/utility', data=data)
    
    def run_group(self, data=None):
        """
        Run a group formula.
        """
        return self.parent._post('formula/run/group', data=data)
    
    def register(self, data=None):
        """
        Register a formula package run.
        """
        return self.parent._post('formula/register', data=data)
    
    def event_set(self, data=None):
        """
        Set a new formula event.
        """
        return self.parent._post('formula/event/set', data=data)
    
    def event_wait(self, data=None):
        """
        Wait for a formula event to be set.
        """
        return self.parent._get('formula/event/wait', data=data)