from lense.portal.ui.handlers import BaseHandlerController

class HandlerController(BaseHandlerController):
    """
    Portal authentication application controller class.
    """ 
    def __init__(self):
        LENSE.PORTAL.ASSETS.handler = 'auth'
        
        # Load the base handler
        super(HandlerController, self).__init__()
    
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Set the template attributes
        LENSE.PORTAL.TEMPLATE.construct({
            'page': {
                'title': 'Lense Login',
                'css': ['auth.css'],
                'contents': ['handlers/auth/tables/login.html']
            }     
        })