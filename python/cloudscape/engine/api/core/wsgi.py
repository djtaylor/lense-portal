import os

"""
CloudScape Server API WSGI Application

This file serves as the entry point for Apache when launching the CloudScape
server API. The CloudScape API handles the majority of database interactions,
and remote connections to managed hosts.
"""

# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloudscape.engine.api.core.settings")

# Start the API WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()