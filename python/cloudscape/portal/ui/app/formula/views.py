# Django Libraries
from django.views.generic import View

class AppModule(View):
    """
    Application view for the CloudScape portal formulas page.
    """
    def get(self, request, *args, **kwargs):
        if not self.portal.authenticated:
            return self.redirect('auth')
        return self.portal.template