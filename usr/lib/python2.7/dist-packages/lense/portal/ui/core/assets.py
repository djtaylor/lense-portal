from lense.common.vars import SHARE
from lense.common.collection import Collection

# Static assets
STATIC = Collection.create({
    'JS':  '{0}/static/js/lense'.format(SHARE.PORTAL),
    'CSS': '{0}/static/css'.format(SHARE.PORTAL)
})

# Core assets
CORE   = Collection.create({
    'JS': {
        'common': {
            'path': '{0}/common'.format(STATIC.JS),
            'relpath': 'js/lense/common'
        },
        'api': {
            'exclude': ['auth'],
            'path': '{0}/api'.format(STATIC.JS),
            'relpath': 'js/lense/api'
        },
        'object': {
            'exclude': ['auth'],
            'path': '{0}/object'.format(STATIC.JS),
            'relpath': 'js/lense/object'
        },
        'template': {
            'exclude': ['auth'],
            'path': '{0}/template'.format(STATIC.JS),
            'relpath': 'js/lense/template'
        }
    }
})

class PortalAssets(object):
    """
    Construct portal assets.
    """
    def __init__(self):

        # JavaScript / CSS assets
        self._js        = {'core': [], 'handler': None}
        self._css       = {'core': [], 'handler': []}

        # Handlerbars templates
        self._templates = []

        # Request handler
        self.handler    = None

    def log(self, msg, level='info'):
        """
        Log wrapper per handler.
        """
        logger = getattr(LENSE.LOG, level, 'info')
        logger('<ASSETS.{0}> {1}'.format(
            LENSE.REQUEST.path,
            msg
        ))

    def _getHandlebars(self):
        """
        Retrieve all available Handlebars.js template assets.
        """
        template_dir = '{0}/templates/handlebars'.format(SHARE.PORTAL)
        templates    = []

        # Get template assets
        self.log('Retrieving Handlebars.js template assets from: {0}'.format(template_dir))
        for template in LENSE.FS.listdir(template_dir):
            templates.append(template.replace('.html.handlebars', ''))
            self.log('Discovered template asset: {0}'.format(template))

        # Store templates
        self._templates = templates

    def _get_HandlerAssets(self):
        """
        Retrieve all assets for the current request path handler.
        """
        asset_dir     = '{0}/handlers/{1}'.format(STATIC.JS, self.handler)
        asset_relpath = 'js/lense/handlers/{0}'.format(self.handler)
        assets        = []

        # Get handler JavaScript assets
        self.log('Retrieving handler JavaScript assets from: {0}'.format(asset_dir))
        for asset in LENSE.FS.listdir(asset_dir):
            assets.append(asset)
            self.log('Discovered JavaScript asset: {0}/{1}'.format(asset_relpath, asset))

        # Interface required
        LENSE.ensure(('interface.js' in assets), isnot = False, error = 'Handler must have a JavaScript interface')

        # Store assets
        self._js['handler'] = ['{0}/{1}'.format(asset_relpath, x) for x in assets]

    def _get_CoreAssets(self):
        """
        Retrieve core static assets for the current request path handler.
        """

        # Get core JavaScript assets
        for asset_key in CORE.JS._fields:
            asset_attrs   = getattr(CORE.JS, asset_key)
            asset_dir     = getattr(asset_attrs, 'path', '{0}/{1}'.format(STATIC.JS, asset_key))
            asset_relpath = getattr(asset_attrs, 'relpath', '/static/js/lense/{0}'.format(asset_key))
            asset_exclude = getattr(asset_attrs, 'exclude', [])

            # Looking for core assets
            self.log('Retrieving core JavaScript assets from: {0}'.format(asset_dir))

            # Load asset files
            for asset in LENSE.FS.listdir(asset_dir):
                asset_path = '{0}/{1}'.format(asset_relpath, asset)

                # If excluding asset
                if LENSE.REQUEST.path in asset_exclude:
                    self.log('Excluding core JavaScript asset: {0}, in_path={1}'.format(asset_path, LENSE.REQUEST.path))
                    continue

                # Store the asset
                self._js['core'].append(asset_path)
                self.log('Discovered core JavaScript asset: {0}'.format(asset_path))

    def _get_assets(self):
        """
        Retrieve static assets for the current request path handler.
        """
        self._get_CoreAssets()
        self._get_HandlerAssets()
        self._get_HandlebarsAssets()

    def construct(self):
        """
        Construct and return static assets for the current request handler.
        """

        # Get all assets
        self._get_assets()

        # Return constructed assets
        return {
            'js':  self._js['core'] + self._js['handler'],
            'css': self._css['core'] + self._css['handler'],
            'templates': self._templates
        }
