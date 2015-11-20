from lense.portal.ui.core.template import PortalTemplate

class HandlerController(PortalTemplate):
    """
    Portal authentication application controller class.
    """
    def __init__(self, parent):
        super(AppController, self).__init__(parent)
        
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Set the template attributes
        self.set_template({
            'state':         getattr(kwargs, 'state', None), 
            'state_display': getattr(kwargs, 'state_display', 'none'),
            'base_path':     self.portal.request.script,
            'page': {
                'title': 'Lense Login',
                'css': ['auth.css'],
                'contents': ['handlers/auth/tables/login.html']
            }     
        })
        
        # Construct and return the template response
        return self.response()