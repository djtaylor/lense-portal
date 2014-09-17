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
                'list': {
                    'data': self._list
                },
                'groups': {
                    'data': self._groups
                },
                'details': {
                    'data': self._details
                }
            },
            'default': 'list'
        }
        
    def _groups(self):
        """
        Construct and return the template data required to render the host groups page.
        """
        
        # Make all required API calls
        response = self.api_call_threaded({
            'hgroups':     ('host', 'get_group'),
            'hosts':       ('host', 'get'),
            'datacenters': ('locations', 'get_datacenters'),
            'formulas':    ('formula', 'get')
        })
        
        # Host groups / target host group / editing flag / host group details
        hgroups_target = self.get_query_key('group')
        hgroups_edit   = self.get_query_key('edit')
        hgroups_detail = None if not hgroups_target else [x for x in response['hgroups'] if x['uuid'] == hgroups_target][0]
        
        def set_contents():
            """
            Set template contents.
            """
            if hgroups_target:
                if hgroups_edit:
                    return ['app/hosts/tables/groups/editor.html']
                return ['app/hosts/tables/groups/details.html']
            return ['app/hosts/tables/groups/list.html']
        
        def set_popups():
            """
            Set template popups.
            """
            if hgroups_target:
                return []
            return [
                'app/hosts/popups/groups/create.html',
                'app/hosts/popups/groups/delete.html' 
            ]
        
        # Return the template data
        return {
            'hgroups': {
                'all':     response['hgroups'],
                'target':  hgroups_target,
                'detail':  hgroups_detail,
                'edit':    hgroups_edit
            },
            'hosts':       response['hosts'],
            'datacenters': response['datacenters'],
            'formulas':    response['formulas'],
            'page': {
                'title':  'CloudScape Host Groups',
                'css': [
                    'hosts/groups.css'
                ],
                'contents': set_contents(),
                'popups':   set_popups()
            }
        }
        
    def _list(self):
        """
        Construct and return the template data required to render the hosts list page.
        """
        
        # Make all required API calls
        response = self.api_call_threaded({
            'hosts':       ('host', 'get'),
            'hgroups':     ('host', 'get_group'),
            'datacenters': ('locations', 'get_datacenters'),
            'dkeys':       ('host', 'get_dkey')
        })
        
        # Return the template data
        return {
            'hosts':       response['hosts'],
            'groups':      response['hgroups'],
            'datacenters': response['datacenters'],
            'dkeys':       response['dkeys'],
            'page': {
                'header': 'Hosts',
                'title':  'CloudScape Hosts',
                'css': [
                    'hosts/list.css'
                ],
                'contents': [
                    'app/hosts/tables/list.html',
                    'app/hosts/tables/filter.html'
                ],
                'popups': [
                    'app/hosts/popups/add.html',
                    'app/hosts/popups/delete.html'
                ]
            }         
        }
        
    def _details(self):
        """
        Construct and return the template data required to render the host details page.
        """
        
        # Make sure a host parameter is supplied
        if not self.request_contains(self.portal.request.get, 'host'):
            return self.set_redirect('/%s?panel=overview' % self.path)
        
        # Make all required API calls
        response = self.api_call_threaded({
            'host':     ('host', 'get', {'uuid':self.portal.request.get.host}),
            'formulas': ('host', 'get_formula', {'uuid':self.portal.request.get.host}),
            'groups':   ('group', 'get')
        })
        
        
        # Make sure host details are retrievable
        if not response['host']:
            return self.set_redirect('/hosts?panel=overview')
        
        # Return the constructed template data
        return {
            'host': {
                'name':     response['host']['name'],
                'details':  response['host'],
                'formulas': response['formulas']
            },
            'groups':       response['groups'],
            'page': {
                'title':  'CloudScape Host - \'%s\'' % response['host']['name'],
                'header': 'Host Details - \'%s\'' % response['host']['name'],
                'css': [
                    'hosts/details.css'
                ],
                'contents': [
                    'app/hosts/tables/sysinfo.html',
                    'app/hosts/tables/formulas.html'
                ],
                'popups': [
                    'app/hosts/popups/formula/remove.html',
                    'app/hosts/popups/formula/params.html',
                    'app/hosts/popups/formula/log.html'
                ]
            }
        }
        
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # If the panel is not supported
        if not self.panel in self.map['panels']:
            return self.redirect('portal/hosts?panel=%s' % self.map['default'])
        
        # Set the template file
        t_file = 'app/hosts/%s.html' % self.panel
        
        # Set the template attributes
        self.set_template(self.map['panels'][self.panel]['data']())
        
        # Construct and return the template response
        return self.response()