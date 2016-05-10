from lense.portal.ui.handlers import BaseHandlerController

class HandlerController(BaseHandlerController):
    """
    Portal formula application controller class.
    """
    def __init__(self):
        LENSE.PORTAL.ASSETS.handler = 'home'
        
        # Load the base handler
        super(HandlerController, self).__init__()
    
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Construct template
        LENSE.PORTAL.TEMPLATE.construct(title='Lense Home')