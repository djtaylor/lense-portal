import time
from datetime import datetime, timedelta

# Django Libraries
from django.conf import settings
from django.contrib import auth

"""
Session Timeouts
"""
class SessionTimeout:
  def process_request(self, request):
    
    # Only attempt session timeout if user is logged in
    if not request.user.is_authenticated() :
      return
  
    # Log the user out when the session expires
    try:
        
        if datetime.now() - request.session['last_touch'] > timedelta(0, int(settings.SESSION_TIMEOUT) * 60, 0):
            auth.logout(request)
            del request.session['last_touch']
            return
    except KeyError:
        pass
    request.session['last_touch'] = datetime.now()