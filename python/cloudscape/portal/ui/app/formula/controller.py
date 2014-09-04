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
        if not self.request_contains(self.portal.request.get, 'formula'):
            return self.set_redirect('/formula?panel=%s' % self.map['default'])
        
        # Check if formula details are retrievable
        ed = self.api_call('editor', 'get', {'uuid': self.portal.request.get.formula})
        if not ed:
            return self.set_redirect('/formula?panel=overview')
        
        # If editing the formula
        formula_edit = 'no'
        if self.request_contains(self.portal.request.get, 'edit', ['yes']):
            formula_edit = 'yes'
   
        # Formula details template data
        base_data = {
            'formula': {
                'state':     self.json.dumps({
                    'locked':    ed['locked'],
                    'locked_by': ed['locked_by']
                }),
                'uuid':      self.portal.request.get.formula,
                'edit':      formula_edit,
                'manifest':  self.json.dumps(ed['manifest']),
                'templates': {},
                'all':       self.api_call('formula', 'get'),
                'name':      ed['name'],
                'label':     ed['label'],
                'desc':      ed['desc']
            },
            'edit': {
                'manifest':  self.json.dumps(ed['manifest']),
                'templates': {}
            },
            'template': {},
            'page': {
                'title': 'Formula - \'%s\'' % ed['name'],
                'css': [
                    'formula/details.css',
                    'css/vendor/chrome.css'
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
        if 'fieldsets' in ed['manifest']:
            for fieldset in ed['manifest']['fieldsets']:
                for field in fieldset['fields']:
                    t_vars[field['name']] = field['desc']
        
        # Available template variables
        base_data['template']['vars'] = t_vars
    
        # Construct a list of templates
        t_names    = []
        t_contents = {}
        for name, encoded in ed['templates'].iteritems():
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
        if not self.request_contains(self.portal.request.get, 'formula'):
            return self.set_redirect('/formula?panel=%s' % self.map['default'])
        
        # Get the formula details
        fd = self.api_call('formula', 'get', {'uuid': self.portal.request.get.formula})
        if not fd:
            return self.set_redirect('/formula?panel=%s' % self.map['default'])
        
        # Get a list of all managed hosts
        mh = self.api_call('host', 'get')
        
        # Construct the hosts template element
        th = {}
        for key, host in enumerate(mh):
            th[host['uuid']] = {
                'type':  host['os_type'],
                'label': '%s: %s %s %s - %s' % (host['name'], host['sys']['os']['distro'], host['sys']['os']['version'], host['sys']['os']['arch'], host['ip'])
            }
        
        # Set the formula requirements and template files
        fr = '' if not 'requires' in fd['manifest']['formula'] else ', '.join(fd['manifest']['formula']['requires'])
        ft = ', '.join(fd['templates'])
        
        # Build a list of the supported operating systems
        fs = []
        for sp in fd['manifest']['formula']['supports']:
            fs.append(sp)
        fs = ', '.join(fs)
        
        # Formula information
        fi = self.OrderedDict([
            ('UUID',      self.portal.request.get.formula),
            ('Name',      fd['name']),
            ('Label',     fd['label']),
            ('Created',   fd['created']),
            ('Modified',  fd['modified']),
            ('Templates', ft),
            ('Requires',  fr),
            ('Supports',  fs)])
        
        # Base template data
        base_data = {
            'formula': {
                'uuid':      self.portal.request.get.formula,
                'name':      fd['name'],
                'label':     fd['label'],
                'desc':      fd['desc'],
                'info':      fi,
                'type':      fd['type'],
                'setgroup':  True if ('setgroup' in fd['manifest']['formula'] and fd['manifest']['formula']['setgroup']) else False,
                'actions':   {} if not ('actions' in fd['manifest']) else fd['manifest']['actions'],
                'fields':    {} if not ('fieldsets' in fd['manifest']) else fd['manifest']['fieldsets'],
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
        if 'fieldsets' in fd['manifest']:
            for fieldset in fd['manifest']['fieldsets']:
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
        
    def construct(self):
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