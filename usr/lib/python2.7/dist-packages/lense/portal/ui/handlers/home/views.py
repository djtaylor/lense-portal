# Django Libraries
from django.views.generic import View

class HandlerView(View):
    """
    Application view for the Lense portal home page.
    """
    
    # Portal object
    portal = None
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal home page.
        """
        if not self.portal.authenticated:
            return self.portal.redirect('/auth')
        return self.portal.template