class HandlerController(object):
    """
    Portal formula application controller class.
    """
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # Construct template
        LENSE.PORTAL.TEMPLATE.construct({
            'page': {
                'title': 'Lense Home',
                'css': [
                    'home.css'
                ]
            }
        })