from lense.portal.ui.core.template import PortalTemplate

class AppController(PortalTemplate):
    """
    Portal API management application controller class.
    """
    def __init__(self, parent):
        super(AppController, self).__init__(parent)
        
        # Construct the request map
        self.map = self._construct_map()
        
    def _construct_map(self):
        """
        Construct the request map.
        """
        return {
            'panels': {
                'connectors': {
                    'data': self._connectors
                },
                'integrators': {
                    'data': self._integrators
                },
                'callbacks': {
                    'data': self._callbacks
                }
            },
            'default': 'connectors'
        }
        
    def _connectors(self):
        response = self.api_call_threaded({
            'connectors':  ('connector', 'get')
        })
        
        # Return the template data
        return {
            'connectors':  response['connectors'],
            'page': {
                'title': 'Lense API Management - Connectors',
                'css': ['apim.css'],
                'contents': [],
                'popups': []
            } 
        }
        
    def _integrators(self):
        response = self.api_call_threaded({
            'integrators':  ('integrator', 'get')
        })
        
        # Return the template data
        return {
            'integrators':  response['integrators'],
            'page': {
                'title': 'Lense API Management - Integrators',
                'css': ['apim.css'],
                'contents': [],
                'popups': []
            } 
        }
        
    def _callbacks(self):
        response = self.api_call_threaded({
            'callbacks':  ('callback', 'get')
        })
        
        # Return the template data
        return {
            'callbacks':  response['callbacks'],
            'page': {
                'title': 'Lense API Management - Callbacks',
                'css': ['apim.css'],
                'contents': [],
                'popups': []
            } 
        }
        
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # If the panel is not supported
        if not self.panel in self.map['panels']:
            return self.redirect('portal/apim?panel={0}'.format(self.map['default']))
        
        # Set the template file
        t_file = 'app/apim/{0}.html'.format(self.panel)
        
        # Set the template attributes
        self.set_template(self.map['panels'][self.panel]['data']())
        
        # Construct and return the template response
        return self.response()