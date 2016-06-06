from lense.portal.ui.handlers import BaseHandlerController

class HandlerController(BaseHandlerController):
    """
    Portal formula application controller class.
    """
    views   = ['manifests']
    default = 'tools?view=manifests'
    
    def __init__(self):
        LENSE.PORTAL.ASSETS.handler = 'tools'
        
        # Load the base handler
        super(HandlerController, self).__init__(
            views   = self.views,
            default = self.default
        )
    
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # No view / invalid view provided
        if not (LENSE.REQUEST.view) or not (LENSE.REQUEST.view in self.views):
            return LENSE.PORTAL.TEMPLATE.construct(redirect=self.default)
        
        # Construct template
        LENSE.PORTAL.TEMPLATE.construct(title='Lense Tools')