import json

# Django Libraries
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

# CloudScape Libraries
from cloudscape.portal.ui.core import utils
from cloudscape.portal.ui.base import PortalBase

class HomeView(View):
    """
    CloudScape portal home.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to the home page.
        """
        
        # Construct the base portal object
        self.portal = PortalBase(__name__).construct(request)
        
        # If the user is not authenticated
        if not self.portal.authenticated:
            return HttpResponseRedirect('/portal/auth')
        
        # Render the home page
        return self.portal.template