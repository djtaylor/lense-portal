from sys import exc_info
from traceback import extract_tb

# Django Libraries
from django.shortcuts import render

# Lense Libraries
from lense import import_class
from lense.portal import PortalBase

class PortalTemplate(PortalBase):
    """
    Class for handling Django template attributes and functionality.
    """
    def __init__(self):

        # User defined template data / requesting user object
        self.data    = {}
        self.user    = LENSE.OBJECTS.USER.get(**{'username': LENSE.REQUEST.USER.name})

        # Assets
        self._assets = {}

    def construct(self, title='Lense Portal', redirect=None):
        """
        Construct portal template attributes.
        """
        handler   = LENSE.PORTAL.ASSETS.handler

        # Template interface / CSS
        interface = 'handlers/{0}/interface.html'.format(handler)
        css       = '{0}.css'.format(handler)

        # If redirecting
        if redirect:
            self.data = self._merge_data({
                'redirect': redirect
            })

        # Normal template construction
        else:
            self.data = self._merge_data({
                'page': {
                    'title':     title,
                    'css':       css,
                    'interface': interface,
                    'view':      'handlers/{0}/{1}.html'.format(handler, LENSE.REQUEST.view)
                }
            })

    def _user_data(self):
        """
        Construct and return user data.
        """
        return {
            'is_admin': LENSE.REQUEST.USER.admin,
            'is_authenticated': LENSE.REQUEST.USER.authorized,
            'groups': getattr(self.user, 'groups', None),
            'email': getattr(self.user, 'email', None),
            'name': getattr(self.user, 'username', None)
        }

    def _request_data(self):
        """
        Construct and return request data.
        """
        return {
            'current': LENSE.REQUEST.current,
            'path': LENSE.REQUEST.path,
            'base': LENSE.REQUEST.script,
            'view': LENSE.REQUEST.view,
        }

    def _navigation(self):
        """
        Return a handler navigation if it exists.
        """
        nav = []

        # Look for handler navigation
        for handler in LENSE.MODULE.handlers(ext='__init__'):
            try:
                handler_nav = import_class('HandlerNavigation', handler['mod'], exit_on_fail=False)
                LENSE.LOG.debug('Loading navigation for handler: {0}'.format(handler['name']))

                # Store the handler navigation
                nav.append(handler_nav.attrs)

            # Handler has no navigation class
            except Exception as e:
                LENSE.LOG.exception('Failed to import handler navigation: {0}'.format(handler['name']))

        # Return constructed navigation
        return nav

    def _api_data(self):
        """
        Construct and return API data.
        """
        return {
            'user': getattr(self.user, 'username', None),
            'group': getattr(self.user, 'groups', None),
            'key': getattr(self.user, 'api_key', None),
            'token': getattr(self.user, 'api_token', None),
            'endpoint': '{0}://{1}:{2}'.format(LENSE.CONF.socket.proto, LENSE.CONF.socket.host, LENSE.CONF.socket.port)
        }

    def _merge_data(self, data={}):
        """
        Merge base template data and page specific template data.
        """

        # Base parameters
        params = {
            'USER': self._user_data(),
            'REQUEST': self._request_data(),
            'API': self._api_data(),
            'ASSETS': self._assets,
            'NAV': self._navigation()
        }

        # Log base template data
        self.log('Constructing base template data: USER={0}, REQUEST={1}, API={2}, ASSETS={3}'.format(
            params['USER'],
            params['REQUEST'],
            params['API'],
            params['ASSETS']
        ), level='debug', method='_merge_data')

        # Merge extra template parameters
        for k,v in data.iteritems():

            # Do not overwrite the 'BASE' key
            if k in ['USER','REQUEST','API', 'LENSE', 'ASSETS']:
                raise RequestError('Template data key "{0}" cannot be overloaded'.format(k), code=500)

            # Append the template data key
            params[k] = v
            self.log('Appending template data: key={0}, value={1}'.format(k,v), level='debug', method='_merge_data')

        # Return the template data object
        return params

    def _include_interface(self, path, exclude=[]):
        """
        Generated include script.
        """
        if LENSE.REQUEST.path in exclude:
            self.log('Skipping include: {0}, in_path={1}'.format(path, LENSE.REQUEST.path))
            return ''
        return 'c.push(\'{0}\');'.format(path)

    def _include_script(self):
        """
        Construct and return the JavaScript include function.
        """

        # Asset includes
        assets = [
            self._include_interface('common.interface'),
            self._include_interface('object.interface', exclude=['auth']),
            self._include_interface('api.interface', exclude=['auth']),
            self._include_interface('template.interface', exclude=['auth']),
            self._include_interface('{0}.interface'.format(LENSE.REQUEST.path))
        ];

        # Includes block
        return '(function() {{ var c = []; {0} lense.bootstrap(c); }})();'.format(' '.join(assets))

    def include(self, data):
        """
        Include static assets for the request handler.
        """

        # Store assets
        for k in ['js', 'css', 'templates']:
            self._assets[k] = data.get(k, [])

        # Construct includes script
        self._assets['INCLUDE'] = self._include_script()

    def response(self):
        """
        Construct and return the template response.
        """

        # If redirecting
        if 'redirect' in self.data:
            self.log('Redirecting -> {0}'.format(self.data['redirect']), level='debug', method='response')
            return LENSE.HTTP.redirect(self.data['redirect'])

        # Return the template response
        try:
            self.log('Return response: interface.html, data={0}'.format(self.data), level='debug', method='response')
            return render(LENSE.REQUEST.DJANGO, 'interface.html', self.data)

        # Failed to render template
        except Exception as e:
            self.log('Internal server error: {0}'.format(str(e)), level='exception', method='response')

            # Get the exception data
            e_type, e_info, e_trace = exc_info()
            e_msg = '{0}: {1}'.format(e_type.__name__, e_info)

            # Return a server error
            return LENSE.HTTP.browser_error('core/error/500.html', {
                'error': 'An error occurred when rendering the requested page',
                'debug': None if not LENSE.CONF.portal.debug else (e_msg, reversed(extract_tb(e_trace)))
            })
