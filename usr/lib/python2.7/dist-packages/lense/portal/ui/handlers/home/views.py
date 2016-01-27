# Django Libraries
from django.views.generic import View

class HandlerView(View):
    """
    Application view for the Lense portal home page.
    """
    def get(self):
        """
        Handle GET requests for the portal home page.
        """
        if not LENSE.PORTAL.authenticated:
            return LENSE.HTTP.redirect('auth')
        return LENSE.PORTAL.template