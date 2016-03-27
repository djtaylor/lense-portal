from lense.portal import PortalBase
from lense import MODULE_ROOT, import_class

class HandlerInterface(PortalBase):
    """
    Class container for handler registration.
    """
    def __init__(self, handler):
        self.handler  = handler

        # Resource includes
        self.includes = {'js': [], 'css': []}

    def __repr__(self):
        return '<{0}.{1}>'.format(self.__class__.__name__, handler)

    def include(self, key, resources=[]):
        """
        Include a static resource (JS/CSS).
        
        :param      key: The resource type key (js/css)
        :type       key: str
        :param resource: The resource type object
        :type  resource: dict
        """
        if not key in ['js', 'css']:
            raise Exception('Invalid resource type: {0}'.format(key))
        
        # JavaScript
        if key == 'js':
            self.includes['js']['interface'] = 'handlers/{0}/interface.js'.format(self.handler)
            
            # Load resources
            for resource in resources:
                self.includes['js'][resource['id']] = resource['path']
            
        # CSS
        if key == 'css':
            pass

class PortalInterface(PortalBase):
    """
    Class for handling template interface construction.
    """
    def __init__(self):
        pass
    
    def bootstrap(self):
        """
        Bootstrap the portal interface.
        """
        for handler in LENSE.MODULE.handlers(ext='__init__'):
            try:
                import_class('register', handler['mod'])
                self.log('Registering handler: {0}'.format(handler['mod']), level='debug', method='bootstrap')
            
            # Could not load register method
            except Exception as e:
                self.log('Failed to register handler "{0}":{1}'.format(handler['mod'], str(e)))
    
    def register(self, handler):
        """
        Allow a handler to register itself.
        
        :param handler: The handler name
        :type  handler: str
        """
        if hasattr(self, handler):
            raise Exception('Cannot overload an already registered handler: {0}'.format(repr(getattr(self, handler))))
        
        # Load the handler
        setattr(self, handler, HandlerInterface(handler))
        self.log('Registering handler interface: {0}'.format(repr(getattr(self, handler))))