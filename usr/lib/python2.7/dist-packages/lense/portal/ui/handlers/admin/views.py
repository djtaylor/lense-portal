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
        if not LENSE.REQUEST.USER.authorized:
            return LENSE.HTTP.redirect('auth')
        return LENSE.PORTAL.TEMPLATE.data