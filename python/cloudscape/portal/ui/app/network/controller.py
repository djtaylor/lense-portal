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
                },
                'switches': {
                    'data': self._switches
                },
                'ipv4blocks': {
                    'data': self._ipv4blocks
                },
                'ipv6blocks': {
                    'data': self._ipv6blocks
                },
                'vlans': {
                    'data': self._vlans
                }
            },
            'default': 'overview'
        }
        
    def _overview(self):
        """
        Construct and return the template data required to render the network overview page.
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
        
    def _vlans(self):
        """
        Construct and return the template data required to render the network VLANs page.
        """
        
        # Look for a target VLAN
        vlan_target = self.get_query_key('vlan')
        
        # Make all required API calls
        response = self.api_call_threaded({
            'datacenters': ('locations', 'get_datacenters')
        })
        
        def set_contents():
            """
            Set table contents.
            """
            if vlan_target:
                return ['app/network/tables/vlans/details.html']
            return ['app/network/tables/vlans/list.html']
            
        def set_popups():
            """
            Set popup contents.
            """
            if vlan_target:
                return []
            return [
                'app/network/popups/vlans/create.html',
                'app/network/popups/vlans/delete.html'
            ]
        
        # Return the template data
        return {
            'vlans': {
                'all':    None,
                'detail': None,
                'target': vlan_target
            },
            'datacenters': response['datacenters'],
            'page': {
                'header': None if not vlan_target else 'Network VLAN: %s' % vlan_target,
                'title':  'CloudScape Network VLANs',
                'contents': set_contents(),
                'popups': set_popups()
            }         
        }
        
    def _ipv6blocks(self):
        """
        Construct and return the template data required to render the network IPv6 blocks page.
        """
        
        # Look for a target block
        block_target = self.get_query_key('block')
        
        # Make all required API calls
        response = self.api_call_threaded({
            'datacenters': ('locations', 'get_datacenters')
        })
        
        def set_contents():
            """
            Set table contents.
            """
            if block_target:
                return ['app/network/tables/ipv6blocks/details.html']
            return ['app/network/tables/ipv6blocks/list.html']
            
        def set_popups():
            """
            Set popup contents.
            """
            if block_target:
                return []
            return [
                'app/network/popups/ipv6blocks/create.html',
                'app/network/popups/ipv6blocks/delete.html'
            ]
        
        # Return the template data
        return {
            'blocks': {
                'all':    None,
                'detail': None,
                'target': block_target
            },
            'datacenters': response['datacenters'],
            'page': {
                'header': None if not block_target else 'Network IPv6 Block: %s' % block_target,
                'title':  'CloudScape Network IPv6 Blocks',
                'contents': set_contents(),
                'popups': set_popups()
            }         
        }
        
    def _ipv4blocks(self):
        """
        Construct and return the template data required to render the network IPv4 blocks page.
        """
        
        # Look for a target block
        block_target = self.get_query_key('block')
        
        # Make all required API calls
        response = self.api_call_threaded({
            'datacenters': ('locations', 'get_datacenters')
        })
        
        def set_contents():
            """
            Set table contents.
            """
            if block_target:
                return ['app/network/tables/ipv4blocks/details.html']
            return ['app/network/tables/ipv4blocks/list.html']
            
        def set_popups():
            """
            Set popup contents.
            """
            if block_target:
                return []
            return [
                'app/network/popups/ipv4blocks/create.html',
                'app/network/popups/ipv4blocks/delete.html'
            ]
        
        # Return the template data
        return {
            'blocks': {
                'all':    None,
                'detail': None,
                'target': block_target
            },
            'datacenters': response['datacenters'],
            'page': {
                'header': None if not block_target else 'Network IPv4 Block: %s' % block_target,
                'title':  'CloudScape Network IPv4 Blocks',
                'contents': set_contents(),
                'popups': set_popups()
            }         
        }
        
    def _switches(self):
        """
        Construct and return the template data required to render the network switches page.
        """
        
        # Look for a target switch
        switch_target = self.get_query_key('router')
        
        # Make all required API calls
        response = self.api_call_threaded({
            'datacenters': ('locations', 'get_datacenters')
        })
        
        def set_contents():
            """
            Set table contents.
            """
            if switch_target:
                return ['app/network/tables/switches/details.html']
            return ['app/network/tables/switches/list.html']
            
        def set_popups():
            """
            Set popup contents.
            """
            if switch_target:
                return []
            return [
                'app/network/popups/switches/create.html',
                'app/network/popups/switches/delete.html'
            ]
        
        # Return the template data
        return {
            'switches': {
                'all':    None,
                'detail': None,
                'target': switch_target
            },
            'datacenters': response['datacenters'],
            'page': {
                'header': None if not switch_target else 'Network Switch: %s' % switch_target,
                'title':  'CloudScape Network Switches',
                'contents': set_contents(),
                'popups': set_popups()
            }         
        }
        
    def _routers(self):
        """
        Construct and return the template data required to render the network routers page.
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