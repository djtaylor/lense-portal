import ldap

# Django Libraries
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
        super(AuthBackendLDAP, self).__init__()
    
    def _map_user_attrs(self, ldap_attrs):
        """
        Map LDAP user attributes to database user attributes.
        """
        
        # Mapped attributes
        mapped = {}
        
        # Map each database attribute
        for d,l in CONFIG.ldap_attr._asdict().iteritems():
            mapped[d] = ldap_attrs[l]
        
        # Return the mapped attributes
        return mapped
    
    def authenticate(self, username, password):
        """
        Authenticate the user and store the encrypted password for default database authentication.
        """
        user = super(AuthBackendLDAP, self).authenticate(username, password)
    
        LOG.info('User authenticated with LDAP backend')
    
        # If the user authentication succeeds, save the password in Django
        if user:
            user.set_password(password)
            user.save()
            
        LOG.info('Returning user object from authenticate method')
        # Return the authenticated user object
        return user
    
    def get_or_create_user(self, username, ldap_user):
        """
        Retrieve or create a user account.
        """
        
        # Map the user attributes
        user_attrs = self._map_user_attrs(ldap_user.attrs)
        
        # Add extra database attributes
        user_attrs.update({
            'from_ldap': True
        })
        
        LOG.info('Mapped user attributes: %s' % str(user_attrs))
        
        # Get the user model
        user_model = get_user_model()
        
        LOG.info('Retrieved user mode, getting or creating user account')
        
        # Get or create the user model and then return
        return user_model.objects.get_or_create(**user_attrs)
    
class AuthBackendInterface(ModelBackend):
    """
    Custom authentication backend to provided mixed database/LDAP support depending on the 
    server configuration.
    """
    def __init__(self):
        
        # Get the usermodel
        self.user_model = get_user_model()
    
    def _user_from_ldap(self, username):
        """
        Check if the user is pulled from the LDAP server.
        """
        if self.user_model.objects.filter(username=username).count():
            return self.user_model.objects.get(username=username).from_ldap
        return None
    
    def _authenticate_ldap(self, username, password):
        """
        Wrapper method for handling LDAP authentication.
        """
        
        # Log the authentication attempt
        LOG.info('Attempting LDAP authentication for user [%s]' % username)
        
        # Try to authenticate the user
        try:
            return AuthBackendLDAP().authenticate(username, password)
            
        # Fallback to database authentication
        except Exception as e:
            LOG.exception('LDAP authentication failed for user [%s]: %s' % (username, str(e)))
            
            # Return the database authentication object
            return self._authenticate_database(username, password)
    
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
        
        # Try to find the user object
        try:
            return self.user_model.objects.get(username=username)
        except self.user_model.DoesNotExist:
            return None
    
    def authenticate(self, username=None, password=None):
        """
        Authenticate a username/password combination.
        """
        
        # If LDAP authentication is configured
        if CONFIG.auth.backend == 'ldap':
            
            # If the user doesn't exist
            if not self.user_model.objects.filter(username=username).count():
                
                # Attempt user authentication
                return self._authenticate_ldap(username, password)
            
            # If the user is from LDAP
            if self._user_from_ldap(username):
                return self._authenticate_ldap(username, password)
                
            # User is not an LDAP account
            else:
                return self._authenticate_database(username, password)
        
        # Using database authentication
        else:
            return self._authenticate_database(username, password)