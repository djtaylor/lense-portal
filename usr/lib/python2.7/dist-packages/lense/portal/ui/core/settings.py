import os

# CloudScape Libraries
from lense.common.vars import TEMPLATES, DB_ENCRYPT_DIR
import lense.common.config as config
from lense.common.auth.utils import AuthGroupsLDAP

# Configuration
CONFIG           = config.parse('PORTAL')

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
ROOT_URLCONF     = 'lense.portal.ui.core.urls'

# API WSGI application
WSGI_APPLICATION = 'lense.portal.ui.core.wsgi.application'

# Template directories
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
           TEMPLATES.PORTAL,
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database connections
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'lense',
        'USER':     CONFIG.db.user,
        'PASSWORD': CONFIG.db.password,
        'HOST':     CONFIG.db.host,
        'PORT':     CONFIG.db.port
    }
}

# Database encryption keys
ENCRYPTED_FIELDS_KEYDIR = DB_ENCRYPT_DIR

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
    'cloudscape.engine.api.app.user',
    'cloudscape.portal.ui.util'
)

# Authentication user model
AUTH_USER_MODEL = 'user.DBUser'

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'cloudscape.common.auth.backends.AuthBackendInterface',
)

# LDAP Authentication
AUTH_LDAP_SERVER_URI = 'ldap://{0}'.format(CONFIG.ldap.host)
AUTH_LDAP_BIND_DN = CONFIG.ldap.user
AUTH_LDAP_BIND_PASSWORD = CONFIG.ldap.password
        
# LDAP user search
AUTH_LDAP_USER_SEARCH = AuthGroupsLDAP.construct()

# Django middleware classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
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
