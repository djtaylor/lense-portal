#!/usr/bin/python
import re
import os
import sys
import apt
import pip
import imp
import pwd
import json
import getpass
import platform
from getpass import getuser, getpass
from subprocess import Popen, PIPE
from cStringIO import StringIO

class _CAPTURE(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

class _BASE(object):
    """
    Base class for sharing a few common methods.
    """
    def __init__(self):
        """
        Common attributes shared by inheriting classes.
        """
        
        # Application user / home directory / default login shell
        self.CS_USER    = 'cloudscape'
        self.CS_HOME    = '/home/cloudscape'
        self.CS_SHELL   = '/bin/bash'
        
        # Get the absolute path to the source code directory
        self.SETUP_PATH = os.path.dirname(os.path.realpath(__file__))
    
        # Try to load the feedback module
        self.feedback   = self._load_feedback()
    
    def chown_dir_recursive(self, path, user):
        """
        Recursively change ownership of a directory.
        """
        
        # Get user attributes
        user_attr = pwd.getpwnam(self.CS_USER)
        
        # Change all files and directories
        for root, dirs, files in os.walk(path):  
            for dir in dirs:  
                os.chown(os.path.join(root, dir), user_attr.pw_uid, user_attr.pw_gid)
            for file in files:
                os.chown(os.path.join(root, file), user_attr.pw_uid, user_attr.pw_gid)
    
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
    
    def _die(self, msg=None, pre=None, post=None):
        
        # Check for a pre-death method
        if callable(pre):
            pre()
        
        # Write the message on stderr
        if msg:
            if hasattr(self.feedback, 'show'):
                self.feedback.show(msg).error()
            else:
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
        
        # Password prompt
        passwd_prompt = lambda: (getpass('Please enter a password: '), getpass('Please confirm the password: '))
        
        # Get a password for the user
        def _get_password():
            passwd, passwd_confirm = passwd_prompt()
            
            # Make sure the passwords match
            if not passwd == passwd_confirm:
                self.feedback.show('Passwords do not match...').error()
                return _get_password()
            return passwd
        
        # Invoke the password prompt
        passwd  = _get_password()
        
        # Add user command
        adduser = ['/usr/sbin/useradd', '-m', '-d', self.CS_HOME, '-s', self.CS_SHELL, self.CS_USER]
        
        # Create the user account
        user_proc = Popen(adduser, stderr=PIPE)
        user_proc.communicate()
        
        # Make sure the account was created
        if not user_proc.returncode == 0:
            self._die('Failed to create user account: %s' % str(proc.stderr))
        self.feedback.show('Created user account "%s"' % self.CS_USER).success()
        
        # Set the user's password
        passwd_proc = Popen(['/usr/sbin/chpasswd'], stderr=PIPE, stdin=PIPE)
        passwd_proc.communicate('%s:%s' % (self.CS_USER, passwd))
        
        # Make sure the password was set
        if not passwd_proc.returncode == 0:
            self._die('Failed to set account password: %s' % str(passwd_proc.stderr))
        self.feedback.show('Set password for user account "%s"' % self.CS_USER).success()
        
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
        
            # Prompt to create the user
            _create_user()
        
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
        
        # Preflight complete
        self.feedback.show('Completed setup preflight checks...').success()

class _SETUP(_BASE):
    
    # APT/PIP/NPM packages
    APT_PKGS = ['apache2', 'python-mysqldb', 'python-dev', 'python-pip', 'python-ldap', 'node', 'nodejs', 'npm']
    PIP_PKGS = ['socketIO-client', 'Django', 'django-encrypted-fields', 'py3compat', 'django-auth-ldap']
    NPM_PKGS = ['socket.io', 'ini', 'winston']

    def __init__(self):
        super(_SETUP, self).__init__()

        # Flag to check if we are using a local MySQL server or not
        self.mysql_use_local = False

    def _set_apache_config(self):
        """
        Update the Apache configuration to read configuration files.
        """
        print '\n' \
        'The setup script can automatically update your Apache\n' \
        'configuration file to include Cloudscape virtual host\n' \
        'configuration files. If you skip this step, you will have\n' \
        'to update the main Apache configuration manually.\n'
        
        # Ask if we should update the Apache config file
        def _update_config_prompt():
            update_rsp = raw_input('Update the Apache configuration file? (y/n): ')
            update_apache = update_rsp.lower()
            if update_apache != 'y' or update_apache != 'n':
                self.feedback.show('Answer must be "y" or "n"...').error()
                return _update_config_prompt
            return True if update_apache == 'y' else False

        # If updating the config file
        if update_apache:
            return
        else:
            self.feedback.show('Skipping Apache configuration...').info()

    def _get_npm_packages(self):
        """
        Get a list of installed NPM packages.
        """
        self.feedback.show('[npm]: Finding installed packages...').info()
        npm_proc = Popen(['npm', '--json', '--prefix', self.CS_HOME, 'ls'], stdout=PIPE, stderr=PIPE)
        npm_stdout, npm_stderr = npm_proc.communicate()

        # If failed to retrieve packages
        if not npm_proc.returncode == 0:
            self._die('[npm]: Failed to discover installed packages...')
        
        # Return a JSON object of installed packages
        json_pkgs = json.loads(npm_stdout)
        if json_pkgs:
            return json_pkgs['dependencies']
        return json_pkgs

    def _check_npm_packages(self):
        """
        Check for required NPM packages.
        """
        
        # Node modules directory
        node_modules_dir = '%s/node_modules' % self.CS_HOME
        
        # Make sure the node_modules directory exists
        if not os.path.isdir(node_modules_dir):
            os.mkdir(node_modules_dir, 0755)
            self.feedback.show('[npm]: Created directory "%s"' % node_modules_dir).info()

        # Construct the package list
        npm_pkgs = self._get_npm_packages()
        
        # Packages to install
        install_pkgs = []
        
        # Process each required package
        self.feedback.show('[npm]: Checking for required packages...').info()
        for pkg_name in self.NPM_PKGS:
            if not pkg_name in npm_pkgs:
                self.feedback.show('[npm]: Marking package "%s" for installation...' % pkg_name).info()
                install_pkgs.append(pkg_name)
            else:
                self.feedback.show('[npm]: Package "%s" already installed...' % pkg_name).info()
    
        # Define the installation command
        install_cmd = ['npm', '--prefix', self.CS_HOME, 'install'] + install_pkgs
    
        # Install any required packages
        if install_pkgs:
            self.feedback.show('[npm]: Installing missing packages...').info()
            npm_proc = Popen(install_cmd, stderr=PIPE)
            npm_proc.communicate()
            
            # Make sure packages were installed
            if not npm_proc.returncode == 0:
                self._die('[npm]: Failed to install missing packages: %s' % str(npm_proc.stderr))
            self.feedback.show('[npm]: Package installation complete...').success()
            
            # Make sure ownership is correct
            self.chown_dir_recursive(node_modules_dir, self.CS_USER)
        else:
            self.feedback.show('[npm]: All packages installed...').info()
    
    def _get_pip_packages(self):
        """
        Get a list of installed PIP packages.
        """
        self.feedback.show('[pip]: Finding installed packages...').info()
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
        self.feedback.show('[pip]: Checking for required packages...').info()
        
        # Make sure required packages are installed
        install_pkgs = []
        for pkg_name in self.PIP_PKGS:
            if not pkg_name in installed_pkgs:
                self.feedback.show('[pip]: Marking package "%s" for installation...' % pkg_name).info()
                install_pkgs.append(pkg_name)
                    
            # Package already installed
            else:
                self.feedback.show('[pip]: Package "%s" already installed...' % pkg_name).info()
        
        # If any packages need to be installed
        if install_pkgs:
            install_cmd = ['install'] + install_pkgs
        
            # Install any required packages
            try:
                self.feedback.show('[pip]: Installing missing packages...').info()
                pip.main(install_cmd)
                self.feedback.show('[pip]: Package installation complete...').success()
                
            # Failed to install package
            except Exception as e:
                self._die('[pip]: Failed to install missing packages: %s' % str(e))
        else:
            self.feedback.show('[pip]: All packages installed...').info()

    def _check_mysql_server(self):
        """
        Give the option to install MySQL server on the local system.
        """
        def _mysql_local_prompt():
            mysql_rsp = raw_input('Would you like to use a MySQL server on the local system? (y/n): ')
            mysql_local = mysql_rsp.lower()
            if mysql_local != 'y' and mysql_local != 'n':
                self.feedback.show('Answer must be "y" or "n"...').error()
                return _mysql_local_prompt()
            return True if mysql_local == 'y' else False

        # Check to see if we should use a local MySQL server
        self.use_mysql_local = _mysql_local_prompt()
        
        # If using a local MySQL server
        if self.use_mysql_local:
            self.APT_PKGS.append('mysql-server')
            self.feedback.show('Using local MySQL server...')
        else:
            self.feedback.show('Not using a local MySQL server...').info()

    def _check_apt_packages(self):
        """
        Install a package via apt-get
        """
        
        # Apt cache object
        self.feedback.show('[apt-get]: Building cache...').info()
        cache = apt.cache.Cache()
        cache.update()
        
        # Flag to run installer
        run_install = False
        
        # Look at each required package
        self.feedback.show('[apt-get]: Checking for required packages...').info()
        for pkg_name in self.APT_PKGS:
            pkg = cache[pkg_name]
            if pkg.is_installed:
                self.feedback.show('[apt-get]: Package "%s" already installed...' % pkg_name).info()
            else:
                run_install = True
                self.feedback.show('[apt-get]: Marking package "%s " for installation' % pkg_name).info()
                pkg.mark_install()
        
        # Install any required packages
        if run_install:
            try:
                self.feedback.show('[apt-get]: Installing missing packages...').info()
                cache.commit()
                self.feedback.show('[apt-get]: Package installation complete...').success()
                
            # Failed to install package
            except Exception as e:
                self._die('[apt-get]: Failed to install missing packages: %s' % str(e))
        else:
            self.feedback.show('[apt-get]: All packages installed...').info()

    def run(self):
        """
        Run the initial setup utility.
        """
        self._check_mysql_server()
        self._check_apt_packages()
        self._check_pip_packages()
        self._check_npm_packages()
        self._set_apache_config()

if __name__ == '__main__':
    
    # Preflight checks
    preflight = _PREFLIGHT()
    preflight.run()
    
    # Run the setup
    setup = _SETUP()
    setup.run()