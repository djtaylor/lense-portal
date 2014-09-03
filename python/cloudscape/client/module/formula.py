"""
CloudScape Formula API Module

API module for handling formula actions which inherits from the APIClient class found
in the manager module. This module is responsible for submitting formula requests to
the API server.
"""
class FormulaAPI:
    def __init__(self, parent):
        self.parent = parent
        
    """
    Create Formula
    
    API method to handle request to the server API to create a new formula.
    """
    def create(self, data={}):
        return self.parent._post(data=data, action='create', path='formula')
    
    """ Run Service Formula """
    def run_service(self, data={}):
        return self.parent._post(data=data, action='service', path='formula/run')
    
    """ Run Utility Formula """
    def run_utility(self, data={}):
        return self.parent._post(data=data, action='utility', path='formula/run')
    
    """ Run Group Formula """
    def run_group(self, data={}):
        return self.parent._post(data=data, action='group', path='formula/run')
    
    """
    Get Formula
    
    API method to return a JSON object of formula details.
    """
    def get(self, data=None):
        return self.parent._get(data=data, action='get', path='formula')
    
    """
    Verify Formula
    
    Verify a formula package by submitting the package UUID, checksum, and
    host UUID.
    """
    def verify(self, data={}):
        return self.parent._get(data=data, action='verify', path='formula')
    
    """
    Register Formula
    
    Register the run of a formula on the target host after verification and
    decryption.
    """
    def register(self, data={}):
        return self.parent._post(data=data, action='register', path='formula')
    
    """ Set Formula Event """
    def event_set(self, data={}):
        return self.parent._post(data=data, action='set', path='formula/event')
    
    """ Wait Formula Event """
    def event_wait(self, data={}):
        return self.parent._get(data=data, action='wait', path='formula/event')
    
    """
    Delete Formula
    
    API method to delete an existing formula in the database.
    """
    def delete(self, data={}):
        return self.parent._post(data=data, action='delete', path='formula')