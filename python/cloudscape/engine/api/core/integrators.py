import pyrax
import pyrax.exceptions as exc

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger

# Configuration / Logger
CONF  = config.parse()
ICONF = config.parse(CONF.integrators.config)
LOG   = logger.create(__name__, CONF.integrators.log)

class _APIRackspace(object):
    def __init__(self, user, key):
        
        pyrax.set_setting("identity_type", "rackspace")
        
        try:
            pyrax.set_credentials(user, key)
        except exc.AuthenticationFailed:
            LOG.exception('Failed to ')

class _APIIntegratorsConfig(object):
    
    def __init__(self):
        
        self.targets = {
            'rackspace': ['user', 'key']
        }

        self.config = None

    def construct(self):
        
        for t, p in self.targets.iteritems():
            if hasattr(ICONF, t):
            
                _target = getattr(t, ICONF)
                _config = {}
                for c in p:
                    _config[c] = getattr(_target, c) 
            
                    user = CONF.integrators.
            
class APIIntegrators(object):
    """
    Third-party API integrators handler. Class designed to handle
    API calls between Rackspace and Cloudscape.
    """
    def __init__(self, rackspace=True):
        
        self.bootstrap = self._bootstrap()
        
    def _bootstrap(self):
        
        self.config = _APIIntegratorsConfig().construct()