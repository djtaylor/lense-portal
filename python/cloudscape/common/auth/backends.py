import ldap

# Django Libraries
from django_auth_ldap.config import LDAPSearch
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_backends, get_user_model

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger

# Configuration / logger
CONFIG = config.parse()
LOG    = logger.create(__name__, CONFIG.utils.log)

# LDAP Parameters
AUTH_LDAP_SERVER_URI    = None
AUTH_LDAP_BIND_DN       = None
AUTH_LDAP_BIND_PASSWORD = None
AUTH_LDAP_USER_SEARCH   = None

class AuthBackendLDAP(LDAPBackend):
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
        
    def authenticate(self, username, password):
        """
        Authenticate the user and store the encrypted password for default database authentication.
        """
        user = LDAPBackend.authenticate(self, username, password)
        
        # If the user authentication succeeds, save the password in Django
        if user:
            user.set_password(password)
            user.save()

        # Return the authenticated user object
        return user
    
    def get_or_create_user(self, username, ldap_user):
        """
        Retrieve or create a user account.
        """
        
        LOG.info('LDAP_USER: %s' % str(dir(ldap_user)))
        
        # Set the kwargs for the user account
        kwargs = {
            'username': username,
            'from_ldap': True
        }
        
        # Get the user model
        user_model = get_user_model()
        
        # Get or create the user model and then return
        return user_model.objects.get_or_create(**kwargs)
    
class AuthBackendInterface(ModelBackend):
    """
    Custom authentication backend to provided mixed database/LDAP support depending on the 
    server configuration.
    """
    
    def _ldap_active(self):
        """
        Check if the LDAP authentication backend is active.
        """
        return AuthBackendLDAP in [b.__class__ for b in get_backends()]
    
    def _authenticate_ldap(self, username, password):
        """
        Wrapper method for handling LDAP authentication.
        """
        
        # Log the authentication attempt
        LOG.info('Attempting LDAP authentication for user [%s]' % username)
        
        # Get the user model
        user_model = get_user_model()
        
        # Try to authenticate the user
        try:
            return AuthBackendLDAP().authenticate(username, password)
            
        # Failed to get the user model
        except:
            return None
    
    def _authenticate_database(self, username, password):
        """
        Wrapper method for handling default database authentication.
        """
        
        # Log the authentication attempt
        LOG.info('Attempting database authentication for user [%s]' % username)
        
        # Return the authentication model
        return ModelBackend.authenticate(self, username, password)
    
    def get_user(self, username):
        """
        Return a user object.
        """
        
        # Get the user model
        user_model = get_user_model()
        
        # Try to find the user object
        try:
            return user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            return None
    
    def authenticate(self, username=None, password=None):
        """
        Authenticate a username/password combination.
        """
        
        # If LDAP authentication is configured
        if CONFIG.auth.backend == 'ldap':
            
            # If the LDAP backend is active
            if self._ldap_active():
                return self._authenticate_ldap(username, password)
                
            # LDAP not active, default to database authentication
            else:
                return self._authenticate_database(username, password)
        
        # Using database authentication
        else:
            return self._authenticate_database(username, password)