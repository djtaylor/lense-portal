class HandlerController(object):
    """
    Portal formula application controller class.
    """
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Set the template attributes
        LENSE.PORTAL.TEMPLATE.construct({
            'page': {
                'title': 'Lense Home',
                'css': [
                    'home.css'
                ]
            }
        })
        
        # Construct and return the template response
        return LENSE.PORTAL.TEMPLATE.response()