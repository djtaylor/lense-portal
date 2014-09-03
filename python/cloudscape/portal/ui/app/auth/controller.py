from cloudscape.portal.ui.core.template import PortalTemplate

class AppController(PortalTemplate):
    """
    Portal authentication application controller class.
    """
    def __init__(self, parent):
        super(AppController, self).__init__(parent)
        
    def construct(self):
        """
        Construct and return the template object.
        """
        
        # Set the template attributes
        self.set_template({
            'state':          None, 
            'state_display': 'none',
            'base_path':      self.portal.request.script,
            'page': {
                'title': 'CloudScape Login',
                'css': ['auth.css'],
                'contents': ['app/auth/tables/login.html']
            }     
        })
        
        # Construct and return the template response
        return self.response()