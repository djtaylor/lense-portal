from cloudscape.portal.ui.core.template import PortalTemplate

class AppController(PortalTemplate):
    """
    Portal formula application controller class.
    """
    def __init__(self, parent):
        super(AppController, self).__init__(parent)
        
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Set the template attributes
        self.set_template({
            'page': {
                'title': 'CloudScape Home',
                'css': [
                    'home.css'
                ]
            }
        })
        
        # Construct and return the template response
        return self.response()