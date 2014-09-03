# Django Libraries
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout

# CloudScape Libraries
from cloudscape.portal.ui.base import PortalBase
from cloudscape.common.collection import Collection

class AuthView(View):
    """
    CloudScape portal authentication.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for logging in and out.
        """
        post_data = Collection(request.POST).get()

        # Change Active Group
        if post_data.action == 'change_group':
            
            # Construct the base portal object
            self.portal = PortalBase(__name__).construct(request)
            
            # Look for a redirect parameter
            redirect    = '/portal/home' if not hasattr(post_data, 'redirect') else post_data.redirect
            
            # Make sure a new group is provided
            if not hasattr(post_data, 'group'):
                return HttpResponseRedirect(redirect)
            
            # Set the new group
            self.portal.set_active_group(post_data.group)
            
            # Redirect to the home page
            return HttpResponseRedirect(redirect)

        # Logout the user
        if post_data.action == 'logout':
            logout(request)
            return HttpResponseRedirect("/portal/auth")
        
        # Login the user
        if post_data.action == 'login':
            username = post_data.username
            password = post_data.password
            
            # Attempt to authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/portal/home")
                else:
                    state = 'Your account is not active - please contact your administrator'
            else:
                state = 'Your username and/or password are incorrect'
        
            # Template data
            template_data = {'state': state, 
                             'state_display': 'block',
                             'username': username, 
                             'base_path': request.META['SCRIPT_NAME']}
        
            # Login failed
            return render_to_response('app/auth/main.html', template_data, context_instance=RequestContext(request))
        
        # Invalid form action
        else:
            raise Exception('Invalid form action supplied in POST data: %s' % post_data.action)
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the authentication page.
        """
        
        # Construct the base portal object
        self.portal = PortalBase(__name__).construct(request)
        
        # If the user is authenticated
        if self.portal.authenticated:
            return HttpResponseRedirect('/portal/home')
            
        # Render the template
        return self.portal.template