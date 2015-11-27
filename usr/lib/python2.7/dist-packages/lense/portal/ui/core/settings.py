import os

# Lense Libraries
from lense.common import config
from lense.common.vars import TEMPLATES
from lense.common.auth.utils import AuthGroupsLDAP

# Project configuration
CONF             = config.parse('PORTAL')

# Project base directory
BASE_DIR         = os.path.dirname(os.path.dirname(__file__))

# Debug mode
DEBUG            = True

# Hosts allowed to use the API
ALLOWED_HOSTS    = []

# Secret key
SECRET_KEY       = CONF.portal.secret

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
        'DIRS': [ TEMPLATES.PORTAL ],
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
        'USER':     CONF.db.user,
        'PASSWORD': CONF.db.password,
        'HOST':     CONF.db.host,
        'PORT':     CONF.db.port
    }
}

# Database encryption keys
ENCRYPTED_FIELDS_KEYDIR = CONF.db.encrypt_dir

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
    'lense.common.objects.user',
    'lense.portal.ui.util'
)

# Authentication user model
AUTH_USER_MODEL = 'user.APIUser'

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'lense.common.auth.backends.AuthBackendInterface',
)

# LDAP Authentication
AUTH_LDAP_SERVER_URI = 'ldap://{0}'.format(CONF.ldap.host)
AUTH_LDAP_BIND_DN = CONF.ldap.user
AUTH_LDAP_BIND_PASSWORD = CONF.ldap.password
        
# LDAP user search
AUTH_LDAP_USER_SEARCH = AuthGroupsLDAP.construct()

# Django middleware classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'lense.portal.ui.core.session.SessionTimeout'
)

# Session serializer
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Session timeout in minutes
SESSION_TIMEOUT = CONF.portal.timeout
