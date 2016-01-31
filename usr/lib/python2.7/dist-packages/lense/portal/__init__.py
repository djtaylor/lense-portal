__version__ = '0.1'

class LensePortal(object):
    """
    Interface class for portal commons.
    """
    def __init__(self):
        
        # Load handlers / controllers
        self.handlers    = LENSE.MODULE.handlers(ext='views', load='HandlerView')
        self.controllers = LENSE.MODULE.handlers(ext='controller', load='HandlerController')
        
        # Bootstrap the portal interface
        self._set_session()
        
    def _set_session(self):
        """
        Set session variables.
        """
        if LENSE.REQUEST.USER.authorized:
            
            # Get the user details
            user   = LENSE.OBJECTS.USER.get(LENSE.REQUEST.USER.name)
            groups = user.groups
            
            # Set the 'is_admin' flag
            LENSE.REQUEST.SESSION.set('is_admin', user.is_admin)
            
            # If the active group hasn't been set yet
            if not LENSE.REQUEST.SESSION.get('active_group'):
                LENSE.REQUEST.SESSION.set('active_group', groups[0]['uuid'])
                
    def set_active_group(self, group):
        """
        Change the session variable for the active API user group.
        """
        user = LENSE.OBJECTS.USER.get(username=LENSE.REQUEST.USER.name)
        
        # Make sure the user is a member of the group
        is_member = False
        for usr_group in user.groups:
            if usr_group['uuid'] == group:
                is_member = True
                break 
        
        # If the group is valid
        if is_member:
            LENSE.REQUEST.SESSION.set('active_group', group)