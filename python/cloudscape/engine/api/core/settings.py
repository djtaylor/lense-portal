import os

"""
CloudScape Server API Django Settings
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

# Internationalization settings
LANGUAGE_CODE    = 'en-us'
TIME_ZONE        = 'UTC'
USE_I18N         = True
USE_L10N         = True
USE_TZ           = True

# API token lifetime in hours
API_TOKEN_LIFE   = 1

# Static files
STATIC_URL       = '/static/'

# URL processor
ROOT_URLCONF     = 'cloudscape.engine.api.core.urls'

# API WSGI application
WSGI_APPLICATION = 'cloudscape.engine.api.core.wsgi.application'

# Formula JSON and API request templates
FORMULA_TEMPLATE = os.path.expandvars('$CLOUDSCAPE_BASE/python/cloudscape/engine/templates/formula/json.template')
API_TEMPLATES    = os.path.expandvars('$CLOUDSCAPE_BASE/python/cloudscape/engine/templates/api')

# Template directories
TEMPLATE_DIRS = (
    os.path.expandvars('$CLOUDSCAPE_BASE/python/cloudscape/engine/templates')
)

# SMTP backend
EMAIL_HOST       = '172.16.100.10'

# Database encryption keys
ENCRYPTED_FIELDS_KEYDIR = os.path.expandvars('$CLOUDSCAPE_BASE/dbkey')

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
    'host_stats': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'cloudscape_host_stats',
        'USER':     'cloudscape',
        'PASSWORD': 'secret',
        'HOST':     'host.example.com',
        'PORT':     '3306'
    }
}

# Managed applications
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudscape.engine.api.app.auth',
    'cloudscape.engine.api.app.formula',
    'cloudscape.engine.api.app.host',
    'cloudscape.engine.api.app.user',
    'cloudscape.engine.api.app.group',
    'cloudscape.engine.api.util.formula',
    'cloudscape.engine.api.app.locations',
    'cloudscape.engine.api.app.cluster',
    'cloudscape.engine.api.app.schedule'
)

# Django middleware classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)