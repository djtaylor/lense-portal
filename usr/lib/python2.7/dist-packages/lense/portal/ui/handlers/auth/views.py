# Django Libraries
from django.views.generic import View

class HandlerView(View):
    """
    Application view for the Lense portal authentication page.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal authentication page.
        """

        # Look for an action parameter
        action = self.portal.POST('action')

        # If no action present
        if not action:
            return self.portal.redirect(self.portal.request.current)

        # Change Active Group
        if action == 'change_group':
            
            # Redirect / group parameter
            redirect = self.portal.POST('redirect', default='/home')
            group    = self.portal.POST('group')
            
            # Make sure a new group is provided
            if not group:
                return self.portal.redirect(redirect)
            
            # Set the new group
            self.portal.set_active_group(group)
            
            # Redirect to the home page
            return self.portal.redirect(redirect)

        # Logout the user
        if action == 'logout':
            return self.portal.logout().redirect('/auth')
        
        # Login the user
        if action == 'login':
            return self.portal.login(username=self.portal.POST('username'), password=self.portal.POST('password'))
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal authentication page.
        """
        
        # If the user is authenticated
        if self.portal.authenticated:
            return self.portal.redirect('/home')
            
        # Render the template
        return self.portal.template