import os

# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lense.portal.ui.core.settings")

# Start the API WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()