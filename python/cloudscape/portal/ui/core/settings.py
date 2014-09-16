import os
from ldap import SCOPE_SUBTREE

# Django Libraries
from django_auth_ldap.config import LDAPSearch

# CloudScape Libraries
import cloudscape.common.config as config

# Configuration
CONFIG           = config.parse()

# Project base directory
BASE_DIR         = os.path.dirname(os.path.dirname(__file__))

# Debug mode
DEBUG            = True
TEMPLATE_DEBUG   = True

# Hosts allowed to use the API
ALLOWED_HOSTS    = []

# Secret key
SECRET_KEY       = CONFIG.portal.secret

# Internationalization settings
LANGUAGE_CODE    = 'en-us'
TIME_ZONE        = 'UTC'
USE_I18N         = True
USE_L10N         = True
USE_TZ           = True

# Static files
STATIC_URL       = '/static/'

# URL processor
ROOT_URLCONF     = 'cloudscape.portal.ui.core.urls'

# API WSGI application
WSGI_APPLICATION = 'cloudscape.portal.ui.core.wsgi.application'

# Template directories
TEMPLATE_DIRS = (
    os.path.expandvars('$CLOUDSCAPE_BASE/python/cloudscape/portal/ui/templates'),
)

# Database connections
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'cloudscape',
        'USER':     CONFIG.db.user,
        'PASSWORD': CONFIG.db.password,
        'HOST':     CONFIG.db.host,
        'PORT':     CONFIG.db.port
    },
    'host_resource': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'cloudscape_host_resource',
        'USER':     CONFIG.db.user,
        'PASSWORD': CONFIG.db.password,
        'HOST':     CONFIG.db.host,
        'PORT':     CONFIG.db.port
    }
}

# Database encryption keys
ENCRYPTED_FIELDS_KEYDIR = os.path.expandvars('$CLOUDSCAPE_BASE/dbkey')

# CORS configuration
CORS_ORIGIN_ALLOW_ALL = True

# Managed applications
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudscape.engine.api.app.user'
)

# Authentication user model
AUTH_USER_MODEL = 'user.DBUser'

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'cloudscape.common.auth.backends.AuthBackendInterface',
)

# LDAP Authentication
AUTH_LDAP_SERVER_URI = CONFIG.ldap.host
AUTH_LDAP_BIND_DN = CONFIG.ldap.user
AUTH_LDAP_BIND_PASSWORD = CONFIG.ldap.password
        
# LDAP user search
AUTH_LDAP_USER_SEARCH = LDAPSearch(CONFIG.ldap.tree, SCOPE_SUBTREE, "(" + CONFIG.ldap.uid_attr + "=%(username)s)")

# Django middleware classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cloudscape.portal.ui.core.session.SessionTimeout'
)

# Session serializer
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Session timeout in minutes
SESSION_TIMEOUT = CONFIG.portal.timeout
