class HandlerController(object):
    """
    Portal administration application controller class.
    """
    def __init__(self):
        
        # Construct the request map
        self.map = self._construct_map()
        
    def _construct_map(self):
        """
        Construct the request map.
        """
        return {
            'panels': {
                'users': {
                    'data': self._users
                },
                'groups': {
                    'data': self._groups
                },
                'acls': {
                    'data': self._acls
                },
                'handlers': {
                    'data': self._handlers,
                },
                'objects': {
                    'data': self._objects
                }
            },
            'default': 'handlers'
        }
        
    def _users(self):
        """
        Helper method used to construct the template data needed to render the users
        administration page.
        """
        
        # Make all required API calls
        response = LENSE.CLIENT.request_threaded({
            'users': ('user', 'GET'),
            'groups': ('group', 'GET')
        })
        
        # Return the template data
        return {
            'users':  response['users'],
            'groups': response['groups'],
            'page': {
                'title': 'Lense Administration - Users',
                'css': ['admin.css'],
                'contents': [
                    'handlers/admin/tables/user/all.html',
                    'handlers/admin/tables/user/details.html'
                ],
                'popups': [
                    'handlers/admin/popups/user/create.html',
                    'handlers/admin/popups/user/reset.html',
                    'handlers/admin/popups/user/disable.html',
                    'handlers/admin/popups/user/enable.html'
                ]
            } 
        }
        
    def _groups(self):
        """
        Helper method used to construct the template data needed to render the groups
        administration page.
        """
               
        # Make all required API calls
        response = LENSE.CLIENT.request_threaded({
            'groups':      ('group', 'GET'),
            'users':       ('user', 'GET'),
            'acl_keys':    ('acl/keys', 'GET'),
            'acl_objects': ('acl/objects', 'GET', {'detailed':True})  
        })
                
        # Target group / group details
        groups_tgt    = LENSE.REQUEST.GET('group')
        groups_detail = None if not groups_tgt else [x for x in response['groups'] if x['uuid'] == groups_tgt][0]
                
        def get_contents():
            """
            Retrieve page contents.
            """
            if groups_tgt:
                return [
                    'handlers/admin/tables/group/overview.html',
                    'handlers/admin/tables/group/permissions.html'
                ]
            return ['handlers/admin/tables/group/list.html']
                
        def get_popups():
            """
            Retrieve page popups.
            """
            if groups_tgt:
                return [
                    'handlers/admin/popups/group/permissions/utilities.html'
                ]
            return [
                'handlers/admin/popups/group/create.html',
                'handlers/admin/popups/group/delete.html'
            ]
                
        # Return the template data 
        return {
            'groups': {
                'all':     response['groups'],
                'target':  groups_tgt,
                'detail':  groups_detail,
                'members': None if not groups_tgt else [x['username'] for x in groups_detail['members']],
                'permissions': {
                    'global': None if not groups_tgt else [x['uuid'] for x in groups_detail['permissions']['global']],
                    'object': None if not groups_tgt else groups_detail['permissions']['object']
                }
            },
            'acls': {
                'all': sorted(response['acls'], key=lambda k: k['name']),
                'objects': response['acl_objects']
            },
            'users': response['users'],
            'page': {
                'title': 'Lense Administration - Groups',
                'css': ['admin.css'],
                'contents': get_contents(),
                'popups': get_popups()
            }          
        }
        
    def _acls(self):
        """
        Helper method used to construct the template data needed to render the ACLs
        administration page.
        """
        
        # Make all required API calls
        response = LENSE.CLIENT.request_threaded({
            'acl_keys': ('acl/keys', 'GET'),
            'handlers': ('handler', 'GET')
        })
        
        # All ACLS / target ACL / target object / target UUID / target utilities list
        acl_all    = sorted(response['acls'], key=lambda k: k['name'])
        acl_target = LENSE.REQUEST.GET('acl')
        acl_obj    = None if not acl_target else [x for x in acl_all if x['uuid'] == acl_target][0]
        acl_utils  = {'global':[],'object':[],'host':[]}
        
        # If rendering a detailed view of a single ACL
        if acl_target:
            for util_type, util_obj in acl_obj['utilities'].iteritems():
                for util in util_obj['list']:
                    acl_utils[util_type].append(util['uuid'])
        
        def set_contents():
            """
            Set template data contents.
            """
            if acl_target:
                return ['handlers/admin/tables/acl/details.html']
            return ['handlers/admin/tables/acl/list.html']
        
        def set_popups():
            """
            Set template data popups.
            """
            if acl_target:
                return []
            return [
                'handlers/admin/popups/acl/create.html',
                'handlers/admin/popups/acl/delete.html'
            ]
        
        # Return the ACL object
        return {
            'acls': {
                'all':       acl_all,
                'target':    acl_target,
                'uuid':      acl_target,
                'detail':    acl_obj,
                'utilities': acl_utils
            },
            'utilities':     sorted(response['utilities'], key=lambda k: k['name']),
            'page': {
                'title': 'Lense Administration - ACLs',
                'css': ['admin.css'],
                'contents': set_contents(),
                'popups':  set_popups()
            }               
        }
        
    def _objects(self):
        """
        Helper method used to construct the template data needed to render the API objects
        administration page.
        """
        
        # Make all required API calls
        response = LENSE.CLIENT.request_threaded({
            'acl_objects': ('acl/objects', 'GET', {'detailed':True}),
            'acl_keys':    ('acl/keys', 'GET')
        })
        
        # All ACL objects / target object / object details
        acl_objects_all    = sorted(response['acl_objects'], key=lambda k: k['name'])
        acl_objects_tgt    = LENSE.REQUEST.GET('object')
        acl_objects_detail = None if not acl_objects_tgt else [x for x in acl_objects_all if x['type'] == acl_objects_tgt][0]
        
        def get_content():
            """
            Get page contents.
            """
            if acl_objects_tgt:
                return [
                    'handlers/admin/tables/objects/overview.html',
                    'handlers/admin/tables/objects/objects.html'
                ]
            return ['handlers/admin/tables/objects/list.html']
        
        def get_popups():
            """
            Get page popups.
            """
            if acl_objects_tgt:
                return []
            return [
                'handlers/admin/popups/objects/create.html',
                'handlers/admin/popups/objects/delete.html'   
            ]
        
        # Return the template data
        return {
            'acls': {
                'objects': {
                    'all':    acl_objects_all,
                    'detail': acl_objects_detail,
                    'target': LENSE.REQUEST.GET('object')
                },
                'all':     sorted(response['acls'], key=lambda k: k['name'])
            },
            'page': {
                'title': 'Lense Administration - Objects',
                'css': ['admin.css'],
                'contents': get_content(),
                'popups': get_popups()
            } 
        }
        
    def _handlers(self):
        """
        Helper method used to construct the template data needed to render the API handlers
        administration page.
        """
        
        # Make all required API calls
        response = LENSE.CLIENT.request_threaded({
            'handlers':    ('handler', 'GET'),
            'acl_objects': ('acl/objects', 'GET')
        })
        
        # All utilities / target utility / utility object
        handler_all = sorted(response['handlers'], key=lambda k: k['name'])
        handler_tgt = LENSE.REQUEST.GET('handler')
        handler_obj = None if not handler_tgt else [x for x in handler_all if x['uuid'] == handler_tgt][0]
        
        # Handler modules / external utilities / ACL objects
        handlers      = []
        modules       = []
        acl_objects   = response['acl_objects']
        
        # Construct modules and utilities
        for handler in handler_all:
            handlers.append(['{0}.{1}'.format(handler['mod'], handler['cls']), handler['cls']])
            if not handler['mod'] in modules:
                modules.append(handler['mod'])
        
        def set_contents():
            """
            Set template data contents.
            """
            if handler_tgt:
                return ['handlers/admin/tables/handlers/details.html']
            return ['handlers/admin/tables/handlers/list.html']
        
        def set_popups():
            """
            Set template data popups.
            """
            if util_tgt:
                return ['handlers/admin/popups/handlers/close.html']
            return [
                'handlers/admin/popups/handlers/create.html',
                'handlers/admin/popups/handlers/delete.html'
            ]
        
        # Return the template data
        return {
            'handlers': {
                'all':    handler_all,
                'target': handler_tgt,
                'uuid':   handler_tgt,
                'detail': handler_obj,
                'edit':   None if not handler_tgt else ('yes' if handler_obj['locked'] else 'no'),
            },
            'modules': modules,
            'methods': ['GET', 'POST', 'PUT', 'DELETE'],
            'handlers': handlers,
            'acl': {
                'objects': acl_objects
            },
            'page': {
                'title': 'Lense Administration - Handler',
                'css': ['admin.css'],
                'contents': set_contents(),
                'popups':  set_popups()
            }           
        }
        
    def construct(self, **kwargs):
        """
        Construct and return the template object.
        """
        
        # If the panel is not supported
        if not self.panel in self.map['panels']:
            return self.redirect('portal/admin?panel={0}'.format(self.map['default']))
        
        # Set the template file
        t_file = 'handlers/admin/{0}.html'.format(self.panel)
        
        # Set the template attributes
        LENSE.PORTAL.TEMPLATE.construct(self.map['panels'][self.panel]['data']())
        
        # Construct and return the template response
        return LENSE.PORTAL.TEMPLATE .response()