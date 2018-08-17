# Django Libraries
from django.views.generic import View

class HandlerView(View):
    """
    Application view for the Lense portal administration page.
    """
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal administration page.
        """
        
        # User is not authorized
        if not LENSE.REQUEST.USER.authorized:
            return LENSE.HTTP.redirect('auth')
        
        # Return the template response
        return LENSE.PORTAL.TEMPLATE.response()