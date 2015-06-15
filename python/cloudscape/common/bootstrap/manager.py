import os
import sys
import json
import shutil
import MySQLdb
from subprocess import Popen
from getpass import getpass

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'cloudscape.engine.api.core.settings'

# cs
from cloudscape.common.feedback import Feedback
from cloudscape.common.vars import L_BASE
from cloudscape.common.cparse import CParse
from cloudscape.engine.api.base import APIBare
from cloudscape.common.bootstrap.params import BootstrapParams
from cloudscape.engine.api.app.group.utils import GroupCreate
from cloudscape.engine.api.app.user.utils import UserCreate
from cloudscape.engine.api.app.gateway.utils import GatewayUtilitiesCreate

class Bootstrap(object):
    """
    Main class object for bootstrapping the Cloudscape installation. This
    includes setting up the database and setting the admin user account.
    """
    def __init__(self):
        self.feedback = Feedback()
    
        # Bootstrap / default administrator parameters
        self.params = BootstrapParams()
        self.admin  = {}
    
        # Database connection
        self._connection = None
    
    def _deploy_config(self):
        """
        Deploy configuration files.
        """
        for f,p in self.params.file['config'].iteritems():
            if not os.path.isfile(p[1]):
                
                # Read the default file content
                c_file = open(p[0], 'r')
                c_str  = c_file.read()
                c_file.close()
                
                # Create the new configuration file
                d_file = open(p[1], 'w')
                d_file.write(c_str)
                d_file.close()
                
                # File deployed
                self.feedback.show('File <%s> deployed' % p[1]).success()
            else:
                self.feedback.show('File <%s> already deployed, skipping...' % p[1]).info()
    
        # Create the log and run directories
        for _dir in ['log', 'run']:
            dir = '%s/%s' % (L_BASE, _dir)
            if not os.path.isdir(dir):
                os.mkdir(dir)
                self.feedback.show('Created directory "%s"' % dir)
            else:
                self.feedback.show('Directory "" already exists, skipping...' % dir)
    
    def _get_password(self, prompt, min_length=8):
        _pass = getpass(prompt)
        
        # Make sure the password is long enough
        if not len(_pass) >= min_length:
            self.feedback.show('Password cannot be empty and must be at least %s characters long' % str(min_length)).error()
            return self._get_password(prompt, min_length)
            
        # Confirm the password
        _pass_confirm = getpass('Please confirm the password: ')
            
        # Make sure the passwords match
        if not _pass == _pass_confirm:
            self.feedback.show('Passwords do not match, try again').error()
            return self._get_password(prompt, min_length)
            
        # Password looks good
        return _pass
    
    def _get_input(self, prompt, default=None):
        _input = raw_input(prompt) or default
        
        # If no input found
        if not _input:
            self.feedback.show('Must provide a value').error()
            return self._get_input(prompt, default)
    
        # Return the input
        return _input
    
    def _try_mysql_root(self):
        """
        Attempt to connect to the MySQL server as root user.
        """
        try:
            self._connection = MySQLdb.connect(
                host=self.params.get_input('db_host'), 
                port=int(self.params.get_input('db_port')),
                user='root',
                passwd=self.params.get_input('db_root_password')
            )
            self.feedback.show('Connected to MySQL using root user').success()
        except Exception as e:
            self.feedback.show('Unable to connect to MySQL with root user: %s' % str(e)).error()
            sys.exit(1)
    
    def _bootstrap_info(self):
        """
        Show a brief introduction and summary on the bootstrapping process.
        """
        print '\nCloudscape Bootstrap Utility\n'
        print 'The bootstrap utility is used to get a new Cloudscape installation up and'
        print 'running as quickly as possible. This will set up the database, make sure'
        print 'any required users exists, and populate the tables with seed data.\n'
    
    def _database_encryption(self):
        """
        Bootstrap the database encryption keys.
        """
        
        # Make sure neither file exists
        if os.path.isfile(self.params.db['encryption']['key']) or os.path.isfile(self.params.db['encryption']['meta']):
            return self.feedback.show('Database encryption key/meta properties already exist').warn()
        
        # Generate the encryption key
        p_keycreate = Popen(['keyczart', 'create', '--location=%s' % self.params.db['encryption']['dir'], '--purpose=crypt'])
        p_keycreate.communicate()
        if not p_keycreate.returncode == 0:
            return self.feedback.show('Failed to create database encryption key').error()
        self.feedback.show('Created database encryption key').success()
    
        # Add the encryption key
        p_keyadd = Popen(['keyczart', 'addkey', '--location=%s' % self.params.db['encryption']['dir'], '--status=primary', '--size=256'])
        p_keyadd.communicate()
        if not p_keyadd.returncode == 0:
            return self.feedback.show('Failed to add database encryption key').error()
        self.feedback.show('Added database encryption key').success()
    
    def _database_seed(self):
        """
        Seed the database with the base information needed to run Cloudscape.
        """
        
        # Create the administrator group
        group = GroupCreate(APIBare(
            data = {
                'uuid': self.params.group['uuid'],
                'name': self.params.group['name'],
                'desc': self.params.group['desc'],
                'protected': self.params.group['protected']
            },
            path = 'group/create'
        )).launch()
        self.feedback.show('Created default Cloudscape administrator group').success()
        
        # Set the new user email/password
        user_email = self.params.get_input('api_admin_email', self.params.user['email'])
        user_passwd = self.params.get_input('api_admin_passwd', self.params.user['password'])
        
        # Create the administrator
        user = UserCreate(APIBare(
            data = {
                'username': self.params.user['username'],
                'group': self.params.user['group'],
                'email': user_email,
                'password': user_passwd,
                'password_confirm': user_passwd
            },
            path = 'user/create'
        )).launch()
        self.feedback.show('Created default Cloudscape administrator account').success()
    
        # Store the administrator details
        self.admin = {
            'username': user['data']['username'],
            'api_key': user['data']['api_key'],
            'uuid': user['data']['uuid'],
            'group': self.params.user['group']
        }
    
        # Create each database utility entry
        for c,a in self.params.util.iteritems():
            utility = GatewayUtilitiesCreate(APIBare(
                data = {
                    'path': a['path'],
                    'desc': a['desc'],
                    'method': a['method'],
                    'mod': a['mod'],
                    'cls': c,
                    'protected': a['protected'],
                    'enabled': a['enabled'],
                    'object': a['object'],
                    'object_key': a['object_key']
                },
                path = 'utilities/create'
            )).launch()
            self.feedback.show('Created database entry for utility "%s": Path=%s, Method=%s' % (c, a['path'], a['method'])).success()
    
    def _read_input(self):
        """
        Read any required user input prompts
        """
        # Run through each parameter
        for p,a in self.params.input.iteritems():
            
            # Regular string input
            if a['type'] == 'str':
                a['value'] = self._get_input(a['prompt'], a['default'])
                
            # Password input
            if a['type'] == 'pass':
                a['value'] = self._get_password(a['prompt'])
        print ''
    
    def _database(self):
        """
        Bootstrap the database and create all required tables and entries.
        """
            
        # Test the database connection
        self._try_mysql_root()
            
        # Create the database and user account
        try:
            _cursor = self._connection.cursor()
            
            # Create the database
            _cursor.execute(self.params.db['query']['create_db'])
            self.feedback.show('Created database "%s"' % self.params.db['attrs']['name']).success()
            
            # Create the database user
            _cursor.execute(self.params.db['query']['create_user'])
            _cursor.execute(self.params.db['query']['grant_user'])
            _cursor.execute(self.params.db['query']['flush_priv'])
            self.feedback.show('Created database user "%s" with grants' % self.params.db['attrs']['user']).success()
            
        except Exception as e:
            self.feedback.show('Failed to bootstrap Cloudscape database: %s' % str(e)).error()
            sys.exit(1)
            
        # Close the connection
        _cursor.close()
        
        # Run Django syncdb
        try:
            app  = '%s/python/cloudscape/engine/api/manage.py' % L_BASE
            proc = Popen(['python', app, 'migrate'])
            proc.communicate()
            
            # Make sure the command ran successfully
            if not proc.returncode == 0:
                self.feedback.show('Failed to sync Django application database').error()
                sys.exit(1)
                
            # Sync success
            self.feedback.show('Synced Django application database').success()
        except Exception as e:
            self.feedback.show('Failed to sync Django application database: %s' % str(e)).error()
            sys.exit(1) 
            
        # Set up database encryption
        self._database_encryption()
            
        # Set up the database seed data
        self._database_seed()
         
    def _update_config(self):
        """
        Update the deployed default server configuration.
        """
        
        # Store the server configuration file
        server_conf   = self.params.file['config']['server_conf'][1]
        
        # Parse and update the configuration
        cp = CParse()
        cp.select(server_conf)
        
        # Update each section
        for section, pair in self.params.get_config(admin_key=self.admin['api_key']).iteritems():
            for key, val in pair.iteritems():
                cp.set_key(key, val, s=section)
                self.feedback.show('[%s] Set key value "%s" for "%s" in section "%s"' % (server_conf, val, key, section)).success()
            
        # Apply the configuration changes
        cp.apply()
        self.feedback.show('Applied updated server configuration').success()
            
    def run(self):
        """
        Kickstart the bootstrap process for Cloudscape.
        """
        
        # Show bootstrap information
        self._bootstrap_info()
        
        # Read user input
        self._read_input()
        
        # Bootstrap the configuration files
        self._deploy_config()
        
        # Bootstrap the database
        self._database()