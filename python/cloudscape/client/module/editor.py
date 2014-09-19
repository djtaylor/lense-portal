class EditorAPI:
    """
    Class wrapper for requests to editor utilities.
    """
    def __init__(self, parent):
        self.parent = parent
    def get(self, data=None):
        """
        Get editor formula and template contents.
        """
        return self.parent._get('editor/get', data=data)
    
    def open(self, data=None):
        """
        Open a formula for editing.
        """
        return self.parent._get('editor/open', data=data)
    
    def close(self, data=None):
        """
        Close a formula and release the editing lock.
        """
        return self.parent._get('editor/close', data=data)
    
    def validate(self, data=None):
        """
        Validate formula and template contents.
        """
        return self.parent._post('editor/validate', data=data)
    
    def save(self, data=None):
        """
        Save formula and template contents.
        """
        return self.parent._post('editor/save', data=data)