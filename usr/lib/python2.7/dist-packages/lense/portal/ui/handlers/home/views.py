# Django Libraries
from django.views.generic import View

class HandlerView(View):
    """
    Application view for the Lense portal home page.
    """
    def get(self, request):
        """
        Handle GET requests for the portal home page.
        """
        
        # User is not authorized, redirect to login page
        if not LENSE.REQUEST.USER.authorized:
            return LENSE.HTTP.redirect('auth')
        
        # Return the template response
        return LENSE.PORTAL.TEMPLATE.response()