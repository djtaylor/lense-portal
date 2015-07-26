import os

"""
CloudScape Portal UI WSGI Application

This file serves as the entry point for Apache when launching the CloudScape
portal web interface. The CloudScape portal is the graphical front-end that interacts
with the server API to perform administrative tasks.
"""

# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloudscape.portal.ui.core.settings")

# Start the API WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()