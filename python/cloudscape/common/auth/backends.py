import ldap
from django_auth_ldap.config import LDAPSearch

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger

# Configuration / logger
CONFIG = config.parse()
LOG    = logger.create(__name__, CONFIG.server.log)

# LDAP Parameters
AUTH_LDAP_SERVER_URI    = None
AUTH_LDAP_BIND_DN       = None
AUTH_LDAP_BIND_PASSWORD = None
AUTH_LDAP_USER_SEARCH   = None

class LDAPBackend(object):
    """
    Class wrapper for querying the LDAP server for authentication.
    """
    def __init__(self):
        
        # Access global variables
        global AUTH_LDAP_SERVER_URI, \
               AUTH_LDAP_BIND_DN, \
               AUTH_LDAP_BIND_PASSWORD, \
               AUTH_LDAP_USER_SEARCH
        
        # LDAP server / bind DN / password
        AUTH_LDAP_SERVER_URI = CONFIG.ldap.host
        AUTH_LDAP_BIND_DN = CONFIG.ldap.user
        AUTH_LDAP_BIND_PASSWORD = CONFIG.ldap.password
        
        # LDAP user search
        AUTH_LDAP_USER_SEARCH = LDAPSearch(CONFIG.ldap.tree, ldap.SCOPE_SUBTREE, "(uid=%(username)s)")
    
def get_auth_backends():
    """
    Get the appropriate authentication backends depending on the server configuration.
    """
    auth_backends = {
        'ldap': (
            'django_auth_ldap.backend.LDAPBackend',
            'django.contrib.auth.backends.ModelBackend',
        ),
        'database': (
            'django.contrib.auth.backends.ModelBackend',
        )
    }
    
    # Make sure a valid backend is configured
    if not CONFIG.auth.backend in auth_backends:
        raise Exception('Invalid authentication backend type [%s]. Valid options are: [%s]' % (CONFIG.auth.backend, ','.join(auth_backends.keys())))
    
    # If using LDAP authentication
    if CONFIG.auth.backend == 'ldap':
        LDAPBackend()
    
    # Return the authentication backend tuple for Django
    return auth_backends[CONFIG.auth.backend]
    