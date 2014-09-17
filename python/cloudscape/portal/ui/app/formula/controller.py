from cloudscape.portal.ui.core.template import PortalTemplate

class AppController(PortalTemplate):
    """
    Portal formulas application controller class.
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
                'details': {
                    'data': self._details
                },
                'run': {
                    'data': self._run
                }
            },
            'default': 'overview'
        }
        
    def _overview(self):
        """
        Construct template data needed to render the formulas overview page.
        """
        fd = self.api_call('formula', 'get')
        
        # Split formulas into service/utility and group formulas
        su_formula = []
        gr_formula = []
        for f in fd:
            if f['type'] == 'group':
                gr_formula.append(f)
            else:
                su_formula.append(f)
        
        # Return the template data
        return {
            'groups':     gr_formula,
            'srv_util':   su_formula,
            'page': {
                'title':  'CloudScape Formulas',
                'header': 'Formulas',
                'css': [
                    'formula/overview.css'
                ],
                'contents': [
                    'app/formula/tables/all.html'
                ],
                'popups': [
                    'app/formula/popups/create.html',
                    'app/formula/popups/delete.html'
                ]
            }               
        }
    
    def _details(self):
        """
        Construct the template data needed to render the formula details page.
        """
        
        # Make sure a formula ID parameter is supplied
        formula = self.portal.GET('formula')
        if not formula:
            return self.set_redirect('/formula?panel=%s' % self.map['default'])
        
        # Make all required API calls
        response = self.api_call_threaded({
            'editor':   ('editor', 'get', {'uuid':formula}),
            'formulas': ('formula', 'get')
        })
        
        # Check if formula details are retrievable
        if not response['editor']:
            return self.set_redirect('/formula?panel=overview')
        
        # If editing the formula
        formula_edit = self.portal.GET('edit')
   
        # Formula details template data
        base_data = {
            'formula': {
                'state':     self.json.dumps({
                    'locked':    response['editor']['locked'],
                    'locked_by': response['editor']['locked_by']
                }),
                'uuid':      formula,
                'edit':      formula_edit,
                'manifest':  self.json.dumps(response['editor']['manifest']),
                'templates': {},
                'all':       response['formulas'],
                'name':      response['editor']['name'],
                'label':     response['editor']['label'],
                'desc':      response['editor']['desc']
            },
            'edit': {
                'manifest':  self.json.dumps(response['editor']['manifest']),
                'templates': {}
            },
            'template': {},
            'page': {
                'title': 'Formula - \'%s\'' % response['editor']['name'],
                'css': [
                    'formula/details.css',
                    'vendor/chrome.css'
                ],
                'contents': [
                    'app/formula/tables/details.html'
                ],
                'popups': [
                    'app/formula/popups/editor/close.html',
                    'app/formula/popups/editor/add_template.html'
                ]
            }
        }
            
        # Construct a list of available template variables
        t_vars = {}
        if 'fieldsets' in response['editor']['manifest']:
            for fieldset in response['editor']['manifest']['fieldsets']:
                for field in fieldset['fields']:
                    t_vars[field['name']] = field['desc']
        
        # Available template variables
        base_data['template']['vars'] = t_vars
    
        # Construct a list of templates
        t_names    = []
        t_contents = {}
        for name, encoded in response['editor']['templates'].iteritems():
            t_names.append(name)
            t_contents[name] = encoded
        
        # Set template names / contents / encoded contents
        base_data['formula']['templates'] = '["' + '","'.join(t_names) + '"]'
        base_data['edit']['templates']    = t_names
        base_data['template']['contents'] = t_contents
        base_data['template']['encoded']  = self.json.dumps(t_contents)
    
        # Return the template data
        return base_data
    
    def _run(self):
        """
        Construct and return the template data required to render the formula run page.
        """
        
        # Make sure a formula ID parameter is supplied
        formula = self.portal.GET('formula')
        if not formula:
            return self.set_redirect('/formula?panel=%s' % self.map['default'])
        
        # Make all required API calls
        response = self.api_call_threaded({
            'formula': ('formula', 'get', {'uuid':formula}),
            'hosts':   ('host', 'get')
        })
        
        # Get the formula details
        if not response['formula']:
            return self.set_redirect('/formula?panel=%s' % self.map['default'])
        
        # Construct the hosts template element
        th = {}
        for host in response['hosts']:
            th[host['uuid']] = {
                'type':  host['os_type'],
                'label': '%s: %s %s %s - %s' % (host['name'], host['sys']['os']['distro'], host['sys']['os']['version'], host['sys']['os']['arch'], host['ip'])
            }
        
        # Set the formula requirements and template files
        fr = '' if not 'requires' in response['formula']['manifest']['formula'] else ', '.join(response['formula']['manifest']['formula']['requires'])
        ft = ', '.join(response['formula']['templates'])
        
        # Build a list of the supported operating systems
        fs = []
        for sp in response['formula']['manifest']['formula']['supports']:
            fs.append(sp)
        fs = ', '.join(fs)
        
        # Formula information
        fi = self.OrderedDict([
            ('UUID',      formula),
            ('Name',      response['formula']['name']),
            ('Label',     response['formula']['label']),
            ('Created',   response['formula']['created']),
            ('Modified',  response['formula']['modified']),
            ('Templates', ft),
            ('Requires',  fr),
            ('Supports',  fs)])
        
        # Base template data
        base_data = {
            'formula': {
                'uuid':      formula,
                'name':      response['formula']['name'],
                'label':     response['formula']['label'],
                'desc':      response['formula']['desc'],
                'info':      fi,
                'type':      response['formula']['type'],
                'setgroup':  True if ('setgroup' in response['formula']['manifest']['formula'] and response['formula']['formula']['manifest']['formula']['setgroup']) else False,
                'actions':   {} if not ('actions' in response['formula']['manifest']) else response['formula']['manifest']['actions'],
                'fields':    {} if not ('fieldsets' in response['formula']['manifest']) else response['formula']['manifest']['fieldsets'],
            },
            'managed_hosts': th,
            'page': {
                'title': 'Run Formula - \'%s\'' % fd['name'],
                'css': [
                    'formula/run.css'
                ],
                'contents': [
                    'app/formula/tables/run.html'
                ]
            }
        }
        
        # Look for any group select menus
        formula_groups = []
        if 'fieldsets' in response['formula']['manifest']:
            for fieldset in response['formula']['manifest']['fieldsets']:
                for field in fieldset['fields']:
                    if (field['type'] == 'select_group') and ('group' in field):
                        kps = field['group'].split(';')
                        for kp in kps:
                            kv = kp.split('=')
                        
                            # Only support formula filters
                            if kv[0] == 'formula':
                                
                                # Get all groups for that formula
                                _groups = self.api_call('host', 'get_group', {'formula': kv[1]})
                                if _groups:
                                    for _group in _groups:
                                        formula_groups.append({
                                            'name': _group['name'],
                                            'uuid': _group['uuid']
                                        })
                                        
        # If any formula groups found
        if formula_groups:
            base_data['formula_groups'] = formula_groups
        
        # Return the template data
        return base_data
        
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # If the panel is not supported
        if not self.panel in self.map['panels']:
            return self.redirect('portal/formula?panel=%s' % self.map['default'])
        
        # Set the template file
        t_file = 'app/formula/%s.html' % self.panel
        
        # Set the template attributes
        self.set_template(self.map['panels'][self.panel]['data']())
        
        # Construct and return the template response
        return self.response()