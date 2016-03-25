class HandlerController(object):
    """
    Portal authentication application controller class.
    """ 
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Set the template attributes
        LENSE.PORTAL.TEMPLATE.construct({
            'page': {
                'title': 'Lense Login',
                'css': ['auth.css'],
                'contents': ['handlers/auth/tables/login.html']
            }     
        })