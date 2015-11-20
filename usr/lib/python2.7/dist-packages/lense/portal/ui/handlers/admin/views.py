# Django Libraries
from django.views.generic import View

class HandlerView(View):
    """
    Application view for the Lense portal administration page.
    """
    
    # Portal object
    portal = None
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal administration page.
        """
        if not self.portal.authenticated:
            return self.portal.redirect('/auth')
        return self.portal.template