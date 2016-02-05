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
        action = LENSE.REQUEST.POST('action')

        # If no action present
        if not action:
            return LENSE.HTTP.redirect(LENSE.REQUEST.current)

        # Change Active Group
        if action == 'change_group':
            
            # Redirect / group parameter
            redirect = LENSE.REQUEST.POST('redirect', default='/home')
            group    = LENSE.REQUEST.POST('group')
            
            # Make sure a new group is provided
            if not group:
                return LENSE.HTTP.redirect(redirect)
            
            # Set the new group
            LENSE.PORTAL.set_active_group(group)
            
            # Redirect to the home page
            return LENSE.HTTP.redirect(redirect)

        # Logout the user
        if action == 'logout':
            LENSE.OBJECTS.USER.logout()
            return LENSE.HTTP.redirect('auth')
        
        # Login the user
        if action == 'login':
            return LENSE.OBJECTS.USER.login()
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal authentication page.
        """
        
        # If the user is authenticated
        if LENSE.REQUEST.USER.authorized:
            return LENSE.HTTP.redirect('home')
            
        # Render the template
        return LENSE.PORTAL.TEMPLATE.response()