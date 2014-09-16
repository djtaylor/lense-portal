import ldap
from django_auth_ldap.config import LDAPSearch

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger

# Bind DN / Password
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""

class LDAPBackend(object):
    """
    Class wrapper for querying the LDAP server for authentication.
    """
    def __init__(self):
        
        # Configuration / logger
        self.conf = config.parse()
        self.log  = logger.create(__name__, self.conf.server.log)
        
        # Set bind DN / password
        self._set_bind_attrs()
        
    def _set_bind_attrs(self):
        """
        Set a bind DN and password if configured.
        """
        if hasattr(self.conf.ldap, 'user') and hasattr(self.conf.ldap, 'password'):
            
            # Access global LDAP variables
            global AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD
            
            # Set the variable values
            AUTH_LDAP_BIND_DN = self.conf.ldap.user
            AUTH_LDAP_BIND_PASSWORD = self.conf.ldap.password
            
    def query_user(self, username):
        """
        Look for an LDAP user.
        """
        return LDAPSearch(self.conf.ldap.tree, ldap.SCOPE_SUBTREE, "(uid=%(username)s)")