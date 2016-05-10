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
        
        # Construct the portal template
        LENSE.PORTAL.TEMPLATE.construct(title='Lense Login')