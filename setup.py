#!/usr/bin/python
import os
import sys
import apt
import pip
import imp
import pwd
import getpass
import platform
from getpass import getuser
from cStringIO import StringIO

# Installation home / feedback module
HOME = os.path.expanduser('~')

def _load_feedback():
    """
    Helper method to load the feedback module.
    """
    

class _BASE(object):
    """
    Base class for sharing a few common methods.
    """
    def __init__(self):
        """
        Common attributes shared by inheriting classes.
        """
        
        # Application user / home directory
        self.CS_USER    = 'cloudscape'
        self.CS_HOME    = '/home/cloudscape'
        
        # Get the absolute path to the source code directory
        self.SETUP_PATH = os.path.dirname(os.path.realpath(__file__))
    
        # Try to load the feedback module
        self.feedback   = self._load_feedback()
    
    def _load_feedback(self):
        """
        Try to load a local copy of the feedback module.
        """
        
        # Define the module path
        mod_path = '%s/python/cloudscape/common/feedback.py' % self.SETUP_PATH
        
        # Try to load the module
        try:
            mod = imp.load_source('feedback', mod_path)
            return mod.Feedback()
        except Exception:
            self._die('Failed to load feedback module, path "%s" not found' % mod_path)
    
    def _die(self, msg='An unknown error has occured', pre=None, post=None):
        
        # Check for a pre-death method
        if callable(pre):
            pre()
        
        # Write the message on stderr
        sys.stderr.write('ERROR: %s\n' % msg)
        
        # Check for a post-death method
        if callable(post):
            post()
        
        # Exit the program
        sys.exit(1)

class _PREFLIGHT(_BASE):
    """
    Basic helper class to do preflight checks for the setup process.
    """
    
    # Supported distributions / versions
    DISTRO_SUPPORT  = ['ubuntu']
    DISTRO_VERSIONS = {
        'ubuntu': ['14.04', '14.10', '15.04']
    }
    
    def __init__(self):
        super(_PREFLIGHT, self).__init__()
        
        # Get the current system information
        self._platform = platform.linux_distribution()
        
        # Linux distribution and version
        self.distro = {
            'name': self._platform[0],
            'id': self._platform[0].lower(),
            'version': self._platform[1]
        }
        
        # Get the active user
        self.user = getuser()
        
    def _show_os_support(self):
        """
        Show supported distributions and versions.
        """
        print 'Supported operating systems:'
        for d,v in self.DISTRO_VERSIONS.iteritems():
            print '> %s: %s' % (d, str(v))

    def _check_os_support(self):
        """
        Check if the current system is supported.
        """

        # Check for a supported distro
        if not self.distro['id'] in self.DISTRO_SUPPORT:
            self._die(
                msg  = 'The current system\'s distribution "%s" is not yet supported' % self.distro['id'],
                post = self._show_os_support
            )

        # Check for a supported version
        if not self.distro['version'] in self.DISTRO_VERSIONS[self.distro['id']]:
            self._die(
                msg  = 'The current system\'s version "%s" is not yet supported' % self.distro['version'],
                post = self._show_os_support
            )
        
        # Operating system supported
        self.feedback.show('Discovered supported operating system: %s %s' % (self.distro['name'], self.distro['version'])).success()
        
    def _cs_create_user(self):
        """
        Helper method to create the cloudscape user account.
        """
        self.feedback.show('Creating user').info()
        
    def _cs_user_exists(self):
        """
        Make sure the cloudscape user account exists.
        """
        
        # User flag
        user_exists = False
        
        # Check if the user account exists
        try:
            pwd.getpwnam(self.CS_USER)
            user_exists = True
        except KeyError:
            pass
        
        # If the user doesn't exist
        if not user_exists:
            def _create_user():
                response    = raw_input('User account "%s" not found. Create the account now? (y/n): ' % self.CS_USER)
                create_user = response.lower()
        
                # Make sure the answer is valid
                if (create_user != 'y') and (create_user != 'n'):
                    self.feedback.show('Answer must be "y" or "n"...').error()
                    _create_user()
                    
                # If skipping user creation
                if create_user == 'n':
                    self.feedback.show('Skipping user creation. User "cloudscape" must exist prior to completing setup').info()
                    sys.exit(0)
                    
                # If creating the user
                if create_user == 'y':
                    self._cs_create_user()
        
        # User exists
        else:
            self.feedback.show('User "%s" found, skipping creation...' % self.CS_USER).info()
        
    def _using_root(self):
        """
        Make sure the administrator is running setup as root.
        """
        if not self.user == 'root':
            return False
        return True
        
    def run(self):
        """
        Run all preflight setup checks.
        """
        self.feedback.show('Cloudscape Setup').info()
        self.feedback.show('--------------------------------').info()
        self.feedback.show('Running setup preflight checks...').info()
        
        # Make sure running as root
        if not self._using_root():
            self._die('Cloudscape setup script must be run as root, using "%s" user' % self.user)

        # Look for a supported operating system
        self._check_os_support()

        # Make sure the cloudscape user account exists
        self._cs_user_exists()

class _CAPTURE(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

class _SETUP(_BASE):
    
    # APT/PIP/NPM packages
    APT_PKGS = ['apache2', 'python-mysqldb', 'python-pip', 'python-ldap', 'node', 'nodejs', 'npm']
    PIP_PKGS = ['socketIO-client', 'django', 'django-encrypted-fields', 'py3compat', 'django-auth-ldap']
    NPM_PKGS = ['socket.io', 'ini', 'winston']

    def __init__(self):
        super(_PREFLIGHT, self).__init__()

    def _get_pip_packages(self):
        """
        Get a list of installed PIP packages.
        """
        with _CAPTURE() as output:
            pip.main(['list'])
            
        # Construct the PIP packages/versions list
        _pkgs = {}
        for pkg in output:
            name = re.compile(r'(^[^ ]*)[ ].*$').sub(r'\g<1>', pkg)
            version = re.compile(r'^[^ ]*[ ]\((.*)\)$').sub(r'\g<1>', pkg)
            _pkgs[name] = version
        return _pkgs
            
    def _check_pip_packages(self):
        """
        Check for required PIP packages.
        """
        installed_pkgs = self._get_pip_packages()

    def _install_apt_package(self, pkg_name, cache):
        """
        Install a package via apt-get
        """
        pkg = cache[pkg_name]
        if pkg.is_installed:
            print "[%s] Package already installed..." % pkg_name
        else:
            pkg.mark_install()

            try:
                cache.commit()
                print "[%s] Installing package..." % pkg_name
            except Exception as e:
                print "[%s] Failed to install package: %s" % (pkg_name, str(e))
                sys.exit(1)

    def _check_apt_packages(self):
        """
        Check for required APT packages.
        """
        cache = apt.cache.Cache()
        cache.update()

        # Look for required packages
        print 'Checking for required apt packages...'
        for _pkg in self.APT_PKGS:
            self._install_apt_package(_pkg, cache)

    def run(self):
        """
        Run the initial setup utility.
        """
        self._check_os_support()

if __name__ == '__main__':
    
    # Preflight checks
    preflight = _PREFLIGHT()
    preflight.run()
    
    #setup = _SETUP()
    #setup.run()