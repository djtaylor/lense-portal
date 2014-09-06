from cloudscape.portal.ui.core.template import PortalTemplate

class AppController(PortalTemplate):
    """
    Portal hosts application controller class.
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
                'overview': {
                    'data': self._overview
                },
                'routers': {
                    'data': self._routers
                }
            },
            'default': 'overview'
        }
        
    def _overview(self):
        """
        Construct and return the template data required to render the host groups page.
        """
        
        # Make all required API calls
        response = self.api_call_threaded({
            'routers':     ('network', 'get_router'),
            'datacenters': ('locations', 'get_datacenters')
        })
        
        # Return the template data
        return {
            'routers': response['routers'],
            'datacenters': response['datacenters'],
            'page': {
                'title':  'CloudScape Network Overview',
                'contents': [
                    'app/network/tables/overview.html'
                ]
            }
        }
        
    def _routers(self):
        """
        Construct and return the template data required to render the hosts list page.
        """
        
        # Look for a target router
        router_target = self.get_query_key('router')
        
        # Make all required API calls
        response = self.api_call_threaded({
            'routers':     ('network', 'get_router'),
            'datacenters': ('locations', 'get_datacenters')
        })
        
        def set_contents():
            """
            Set table contents.
            """
            if router_target:
                return ['app/network/tables/routers/details.html']
            return ['app/network/tables/routers/list.html']
            
        def set_popups():
            """
            Set popup contents.
            """
            if router_target:
                return []
            return [
                'app/network/popups/routers/create.html',
                'app/network/popups/routers/delete.html'
            ]
        
        # Return the template data
        return {
            'routers': {
                'all':    response['routers'],
                'detail': None if not router_target else [x for x in response['routers'] if x['uuid'] == router_target][0],
                'target': router_target
            },
            'datacenters': response['datacenters'],
            'page': {
                'header': None if not router_target else 'Network Router: %s' % router_target,
                'title':  'CloudScape Network Routers',
                'contents': set_contents(),
                'popups': set_popups()
            }         
        }
        
    def construct(self):
        """
        Construct and return the template object.
        """
        
        # If the panel is not supported
        if not self.panel in self.map['panels']:
            return self.redirect('portal/network?panel=%s' % self.map['default'])
        
        # Set the template file
        t_file = 'app/network/%s.html' % self.panel
        
        # Set the template attributes
        self.set_template(self.map['panels'][self.panel]['data']())
        
        # Construct and return the template response
        return self.response()