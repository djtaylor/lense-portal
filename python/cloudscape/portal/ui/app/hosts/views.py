# Django Libraries
from django.views.generic import View

class AppModule(View):
    """
    Application view for the CloudScape portal hosts page.
    """
    
    # Portal object
    portal = None
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal hosts page.
        """
        if not self.portal.authenticated:
            return self.portal.redirect('/auth')
        return self.portal.template