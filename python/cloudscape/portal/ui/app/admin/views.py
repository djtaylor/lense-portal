import os
import json
import uuid

# Django Libraries
from django.views.generic import View
from django.http import HttpResponseRedirect

# CloudScape Libraries
from cloudscape.portal.ui.core import utils
from cloudscape.portal.ui.base import PortalBase
from cloudscape.common.collection import Collection
from cloudscape.portal.ui.core.api import APIClient

class AdminView(View):
    
    # Handle GET requests and rendering the home page
    def get(self, request, *args, **kwargs):
        
        # Construct the base portal object
        self.portal = PortalBase(__name__).construct(request)
        
        # If the user is not authenticated
        if not self.portal.authenticated:
            return HttpResponseRedirect('/auth')
            
        # Render the template
        return self.portal.template