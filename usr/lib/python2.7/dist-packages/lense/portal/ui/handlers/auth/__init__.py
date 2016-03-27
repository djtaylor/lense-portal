def register():
    """
    Register the authentication handler.
    """
    LENSE.PORTAL.INTERFACE.register('auth')
    LENSE.PORTAL.INTERFACE.auth.include('js')