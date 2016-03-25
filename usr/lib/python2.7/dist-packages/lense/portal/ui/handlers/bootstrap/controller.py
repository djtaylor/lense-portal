class HandlerController(object):
    """
    Portal bootstrap application controller class.
    """
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Construct template
        LENSE.PORTAL.TEMPLATE.construct()