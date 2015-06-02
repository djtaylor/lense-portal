# Installation libraries
from util import CloudScapeUtils

# Default configuration values
_CONFIG = {
    'paths': {
        'base':  '/opt/cloudscape',
        'dbkey': '/opt/cloudscape/dbkey',
        'log':   '/var/log/cloudscape'
    },
    'database': {
        'host': 'localhost',
        'port': 3306,
        'user': 'root'
    }
}

class CloudScapeConfig(object):
    """
    Object used to store user/default configuration values.
    """
    def __init__(self):
        
        # Configuration file / parsed object
        self._ci = self._config_exists()
        self._co = None
        
    def _config_exists(self):
        if not os.path.isfile('../config.ini'):
            return False
        return True

    def construct(self):
        if not self._ci:
            return Collection(_CONFIG).get()
        return config.parse('../config.ini')