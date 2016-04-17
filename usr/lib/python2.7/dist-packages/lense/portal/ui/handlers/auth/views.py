# Django Libraries


# Lense Libraries
from lense.common.exceptions import AuthError
from lense.portal.ui.handlers import BaseHandlerView

class HandlerView(BaseHandlerView):
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
            try:
            
                # Log the user in
                return LENSE.OBJECTS.USER.login(LENSE.REQUEST.POST('username'), LENSE.REQUEST.POST('password'))
            
            # Authentication error
            except AuthError as e:
                return LENSE.HTTP.redirect('auth', 'error={0}'.format(str(e)))
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the portal authentication page.
        """
        
        # If bootstrapping the session
        if LENSE.REQUEST.data.get('bootstrap', False):
            self.log('Bootstrapping authenticated session', level='debug')
            return LENSE.PORTAL.TEMPLATE.response()
        
        # If the user is authenticated
        if LENSE.REQUEST.USER.authorized:
            return LENSE.HTTP.redirect('home')
            
        # Render the template
        return LENSE.PORTAL.TEMPLATE.response()