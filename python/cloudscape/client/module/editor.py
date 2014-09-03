"""
CloudScape Editor API Module
"""
class EditorAPI:
    def __init__(self, parent):
        self.parent = parent
        
    """
    Get Formula Editor Contents
    """
    def get(self, data={}):
        return self.parent._get(data=data, action='get', path='editor')
    
    """
    Open Formula Editor
    """
    def open(self, data={}):
        return self.parent._get(data=data, action='open', path='editor')
    
    """
    Close Formula Editor
    """
    def close(self, data={}):
        return self.parent._get(data=data, action='close', path='editor')
    
    """
    Validate Formula Contents
    """
    def validate(self, data={}):
        return self.parent._post(data=data, action='validate', path='editor')
    
    """
    Save Formula Editor
    """
    def save(self, data={}):
        return self.parent._post(data=data, action='save', path='editor')