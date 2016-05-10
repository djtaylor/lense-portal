from django.views.generic import View

class BaseHandlerController(View):
    """
    Base handler controller.
    """
    def __init__(self, views=[], default=None):
    
        # Handler views / default page
        self.views   = views
        self.default = default if default else LENSE.PORTAL.ASSETS.handler
    
        # Bootstrap the handler
        self._bootstrap()
    
    def _bootstrap(self):
        """
        Bootstrap the requested handler.
        """
        LENSE.PORTAL.TEMPLATE.include(LENSE.PORTAL.ASSETS.construct())
    
    def log(self, msg, level='info'):
        """
        Log wrapper per handler.
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<CONTROLLER:{0}:{1}.{2}> {3}'.format(
            self.__class__.__name__,
            LENSE.REQUEST.method.upper(),
            LENSE.REQUEST.path, 
            msg
        ))

class BaseHandlerView(View):
    """
    Base handler view.
    """
    def log(self, msg, level='info'):
        """
        Log wrapper per handler.
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<VIEW:{0}:{1}.{2}> {3}'.format(
            self.__class__.__name__,
            LENSE.REQUEST.method.upper(),
            LENSE.REQUEST.path, 
            msg
        ))