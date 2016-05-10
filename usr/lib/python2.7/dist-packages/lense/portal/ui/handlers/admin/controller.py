from lense.portal.ui.handlers import BaseHandlerController

class HandlerController(BaseHandlerController):
    """
    Portal formula application controller class.
    """
    views   = ['users', 'groups', 'acls', 'handlers']
    default = 'admin?view=users'
    
    def __init__(self):
        LENSE.PORTAL.ASSETS.handler = 'admin'
        
        # Load the base handler
        super(HandlerController, self).__init__(
            views   = ['users', 'groups', 'acls', 'handlers'],
            default = 'admin?view=users'
        )
    
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        LENSE.LOG.debug('VIEW: {0}'.format(LENSE.REQUEST.view))
        
        # No view / invalid view provided
        if not (LENSE.REQUEST.view) or not (LENSE.REQUEST.view in self.views):
            return LENSE.HTTP.redirect(self.default)
        
        # Construct template
        LENSE.PORTAL.TEMPLATE.construct(title='Lense Administration')