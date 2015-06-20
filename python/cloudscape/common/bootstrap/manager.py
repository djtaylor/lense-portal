import os
import sys
import json
import shutil
import django
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

class Bootstrap(object):
    """
    Main class object for bootstrapping the Cloudscape installation. This
    includes setting up the database and setting the admin user account.
    """
    def __init__(self):
        self.feedback = Feedback()
    
        # Bootstrap parameters
        self.params = BootstrapParams()
    
        # Server configuration file
        self.server_conf = self.params.file['config']['server_conf'][1]
        
        # Database connection
        self._connection = None
    
    def _die(self, msg):
        """
        Quit the program
        """
        self.feedback.show(msg).error()
        sys.exit(1)
    
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
                self.feedback.show('Directory "%s" already exists, skipping...' % dir)
    
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
        return _pass
    
    def _get_input(self, prompt, default=None):
        _input = raw_input(prompt) or default
        
        # If no input found
        if not _input:
            self.feedback.show('Must provide a value').error()
            return self._get_input(prompt, default)
        return _input
    
    def _try_mysql_root(self):
        """
        Attempt to connect to the MySQL server as root user.
        """
        try:
            self._connection = MySQLdb.connect(
                host   = self.params.input.response.get('db_host'), 
                port   = int(self.params.input.response.get('db_port')),
                user   = 'root',
                passwd = self.params.input.response.get('db_root_password')
            )
            self.feedback.show('Connected to MySQL using root user').success()
        except Exception as e:
            self._die('Unable to connect to MySQL with root user: %s' % str(e))
    
    def _bootstrap_complete(self):
        """
        Brief summary of the completed bootstrap process.
        """
        
        # Portal address
        portal_addr = 'http://%s:%s/' % (
            self.params.input.response.get('portal_host'),
            self.params.input.response.get('portal_port')
        )
        
        # Print the summary
        print '\nCloudscape bootstrap complete!\n'
        print 'To start all Cloudscape processes, run "cloudscape-server start".\n'
        print 'You may access the portal using the "cloudscape" user with the password'
        print 'created during the bootstrap process (%s)\n' % portal_addr
        sys.exit(0)
    
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
        
        # Encryption attributes
        enc_attrs = {
            'key': self.params.db['attrs']['encryption']['key'],
            'meta': self.params.db['attrs']['encryption']['meta'],
            'dir': self.params.db['attrs']['encryption']['dir']
        }
        
        # Make sure neither file exists
        if os.path.isfile(enc_attrs['key']) or os.path.isfile(enc_attrs['meta']):
            return self.feedback.show('Database encryption key/meta properties already exist').warn()
        
        # Generate the encryption key
        p_keycreate = Popen(['keyczart', 'create', '--location=%s' % enc_attrs['dir'], '--purpose=crypt'])
        p_keycreate.communicate()
        if not p_keycreate.returncode == 0:
            return self.feedback.show('Failed to create database encryption key').error()
        self.feedback.show('Created database encryption key').success()
    
        # Add the encryption key
        p_keyadd = Popen(['keyczart', 'addkey', '--location=%s' % enc_attrs['dir'], '--status=primary', '--size=256'])
        p_keyadd.communicate()
        if not p_keyadd.returncode == 0:
            return self.feedback.show('Failed to add database encryption key').error()
        self.feedback.show('Added database encryption key').success()
    
    def _database_seed(self):
        """
        Seed the database with the base information needed to run Cloudscape.
        """
        
        # Import modules now to get the new configuration
        from cloudscape.engine.api.app.group.utils import GroupCreate
        from cloudscape.engine.api.app.user.utils import UserCreate
        from cloudscape.engine.api.app.gateway.utils import GatewayUtilitiesCreate, GatewayACLObjectsCreate, GatewayACLCreate
        
        # Setup Django models
        django.setup()
        
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
        
        # If the group was not created
        if not group['valid']:
            self._die('HTTP %s: %s' % (group['code'], group['content']))
        self.feedback.show('Created default Cloudscape administrator group').success()
        
        # Set the new user email/password
        user_email = self.params.input.response.get('api_admin_email', self.params.user['email'])
        user_passwd = self.params.input.response.get('api_admin_password', self.params.user['password'])
        
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
        
        # If the user was not created
        if not user['valid']:
            self._die('HTTP %s: %s' % (user['code'], user['content']))
        self.feedback.show('Created default Cloudscape administrator account').success()
    
        # Update administrator info in the server configuration
        cp = CParse()
        cp.select(self.server_conf)
        cp.set_key('user', user['data']['username'], s='admin')
        cp.set_key('group', self.params.user['group'], s='admin')
        cp.set_key('key', user['data']['api_key'], s='admin')
        cp.apply()
        self.feedback.show('[%s] Set API administrator values' % self.server_conf).success()
    
        # Create each database utility entry
        for c,a in self.params.utils.iteritems():
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
                    'object_key': a['object_key'],
                    'rmap': json.dumps(a['rmap'])
                },
                path = 'utilities'
            )).launch()
            
            # If the utility was not created
            if not utility['valid']:
                self._die('HTTP %s: %s' % (utility['code'], utility['content']))
            self.feedback.show('Created database entry for utility "%s": Path=%s, Method=%s' % (c, a['path'], a['method'])).success()
    
    
        # Create each ACL object entry
        for key, obj in self.params.acl.objects.iteritems():
            acl_obj = GatewayACLObjectsCreate(APIBare(
                data = {
                    "type": obj['type'],
                    "name": obj['name'],
                    "acl_mod": obj['acl_mod'],
                    "acl_cls": obj['acl_cls'],
                    "acl_key": obj['acl_key'],
                    "obj_mod": obj['obj_mod'],
                    "obj_cls": obj['obj_cls'],
                    "obj_key": obj['obj_key'],
                    "def_acl": obj['def_acl']
                },
                path = 'gateway/acl/objects'
            )).launch()
            
            # If the ACL object was not created
            if not acl_obj['valid']:
                self._die('HTTP %s: %s' % (acl_obj['code'], acl_obj['content']))
            self.feedback.show('Created database entry for ACL object "%s->%s"' % (obj['type'], obj['name'])).success()
            
        # Create each ACL key entry
        for key, obj in self.params.acl.keys.iteritems():
            acl_key = GatewayACLCreate(APIBare(
                data = {
                    "name": obj['name'],
                    "desc": obj['desc'],
                    "type_object": obj['type_object'],
                    "type_global": obj['type_global']
                },
                path = 'gateway/acl/objects'
            )).launch()
            
            # If the ACL key was not created
            if not acl_key['valid']:
                self._die('HTTP %s: %s' % (acl_key['code'], acl_key['content']))
            self.feedback.show('Created database entry for ACL key "%s"' % obj['name']).success()
    
    def _read_input(self):
        """
        Read any required user input prompts
        """
        
        # Process each configuration section
        for section, obj in self.params.input.prompt.iteritems():
            print obj['label']
            print '-' * 20
        
            # Process each section input
            for key, attrs in obj['attrs'].iteritems():
                
                # Regular string input
                if attrs['type'] == 'str':
                    val = self._get_input(attrs['prompt'], attrs['default'])
                    
                # Password input
                if attrs['type'] == 'pass':
                    val = self._get_password(attrs['prompt'])
            
            
                # Store in response object
                self.params.input.set_response(key, val)
            print ''
        
        # Update and set database bootstrap attributes
        self.params.set_db()
    
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
            self._die('Failed to bootstrap Cloudscape database: %s' % str(e))
            
        # Close the connection
        _cursor.close()
        
        # Run Django syncdb
        try:
            app  = '%s/python/cloudscape/engine/api/manage.py' % L_BASE
            proc = Popen(['python', app, 'migrate'])
            proc.communicate()
            
            # Make sure the command ran successfully
            if not proc.returncode == 0:
                self._die('Failed to sync Django application database')
                
            # Sync success
            self.feedback.show('Synced Django application database').success()
        except Exception as e:
            self._die('Failed to sync Django application database: %s' % str(e))
            
        # Set up database encryption
        self._database_encryption()
            
        # Set up the database seed data
        self._database_seed()
         
    def _update_config(self):
        """
        Update the deployed default server configuration.
        """
        
        # Parse and update the configuration
        cp = CParse()
        cp.select(self.server_conf)
        
        # Update each section
        for section, pair in self.params.get_config().iteritems():
            for key, val in pair.iteritems():
                cp.set_key(key, val, s=section)
                
                # Format the value output
                self.feedback.show('[%s] Set key value for "%s->%s"' % (self.server_conf, section, key)).success()
            
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
        
        # Bootstrap the configuration files and update
        self._deploy_config()
        self._update_config()
        
        # Bootstrap the database
        self._database()
        
        # Bootstrap complete
        self._bootstrap_complete()