# Django Libraries
from django.views.generic import View

class AppModule(View):
    """
    Application view for the Lense portal API management page.
    """
    
    # Portal object
    portal = None
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal API management page.
        """
        if not self.portal.authenticated:
            return self.portal.redirect('/apim')
        return self.portal.template