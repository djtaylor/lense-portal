import os

"""
CloudScape Portal UI Django Settings
"""

# Project base directory
BASE_DIR         = os.path.dirname(os.path.dirname(__file__))

# Debug mode
DEBUG            = True
TEMPLATE_DEBUG   = True

# Hosts allowed to use the API
ALLOWED_HOSTS    = []

# Secret key
SECRET_KEY       = ''

# API settings
API_HOST         = 'host.example.com'
API_PROTO        = 'http'
API_PORT         = '10550'

# Socket.IO server
SIO_HOST         = 'host.example.com'
SIO_PROTO        = 'http'
SIO_PORT         = '10551'

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
    os.path.expandvars('$CLOUDSCAPE_BASE/python/cloudscape/portal/ui/templates')
)

# Database connections
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'cloudscape',
        'USER':     'cloudscape',
        'PASSWORD': 'secret',
        'HOST':     'host.example.com',
        'PORT':     '3306'
    },
    'host_resource': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'cloudscape_host_resource',
        'USER':     'cloudscape',
        'PASSWORD': 'secret',
        'HOST':     'host.example.com',
        'PORT':     '3306'
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
    'corsheaders',
    'cloudscape.portal.ui.app.auth'
)

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
SESSION_TIMEOUT = 60
