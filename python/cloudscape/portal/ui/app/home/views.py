# Django Libraries
from django.views.generic import View

# CloudScape Libraries
from cloudscape.portal.ui.base import AppBase

class AppModule(AppBase, View):
    """
    Application view for the CloudScape portal home page.
    """
    def __init__(self, request):
        AppBase.__init__(self, request)
    
    def get(self, request, *args, **kwargs):
        if not self.portal.authenticated:
            return self.redirect('auth')
        return self.portal.template