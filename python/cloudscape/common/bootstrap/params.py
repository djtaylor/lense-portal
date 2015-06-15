# cs
from cloudscape.common.utils import rstring
from cloudscape.common.vars import G_ADMIN, U_ADMIN, L_BASE
from cloudscape.common.http import HTTP_GET, HTTP_POST, HTTP_PUT, HTTP_DELETE

class BootstrapParams(object):
    """
    Bootstrap parameters class object used to store and set the attributes
    required when using the bootstrap manager.
    """
    def __init__(self):
        
        # Input/groups/users/database/file parameters
        self.input = self._set_input()
        self.group = self._set_group()
        self.user  = self._set_user()
        self.utils = self._set_utils()
        self.file  = self._set_file()
        self.db    = self._set_db()
    
    def get_config(self, admin_key=None):
        """
        Load the updated server configuration
        """
        
        # Generate a new Django secret for the engine and portal
        engine_secret = "'%s'" % rstring(64)
        portal_secret = "'%s'" % rstring(64)
        
        # Return the updated server configuration
        return {
            'admin': {
                'key': admin_key
            },
            'server': {
                'host': self.get_input('api_host'),
                'port': self.get_input('api_port'),
                'secret': engine_secret      
            },
            'database': {
                'host': self.get_input('db_host'),
                'port': self.get_input('db_port'),
                'user': self.get_input('db_user'),
                'password': self.get_input('db_password')
            },
            'portal': {
                'host': self.get_input('portal_host'),
                'port': self.get_input('portal_port'),
                'secret': portal_secret
            },
            'socket': {
                'host': self.get_input('socket_host'),
                'port': self.get_input('socket_port'),
                'bind_ip': self.get_input('socket_bind_ipaddr')
            }    
        }
    
    def _set_db(self):
        """
        Set default database queries.
        """
        
        # Database attributes
        db_attrs = {
            'name': self.get_input('db_name'),
            'user': self.get_input('db_user'),
            'host': self.get_input('db_host'),
            'passwd': self.get_input('db_password'),
            'encryption': {
                'dir': '%s/dbkey' % L_BASE,
                'key': '%s/dbkey/1' % L_BASE,
                'meta': '%s/dbkey/meta' % L_BASE
            }
        }
        
        # Return the database queries
        return {
            "attrs": db_attrs,
            "query": {
                "create_db": "CREATE DATABASE IF NOT EXISTS %s" % db_attrs['name'],
                "create_user": "CREATE USER '%s'@'%s' IDENTIFIED BY '%s'" % (db_attrs['user'], db_attrs['host'], db_attrs['passwd']),
                "grant_user": "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s'" % (db_attrs['user'], db_attrs['host'], db_attrs['passwd']),
                "flush_priv": "FLUSH PRIVILEGES"
            }
        }
    
    def _set_path(self, path):
        """
        Return a path after prepending L_BASE
        """
        return '%s/%s' % (L_BASE, path)
    
    def _set_file(self):
        """
        Set file deployment parameters.
        """
        return {
            "config": {
                "server_conf": [self._set_path("conf/default/server.conf"), self._set_path("conf/server.conf")],
                "apache_engine": [self._set_path("conf/apache/default/engine.conf"), self._set_path("conf/apache/engine.conf")],
                "apache_portal": [self._set_path("conf/apache/default/portal.conf"), self._set_path("conf/apache/portal.conf")]
            }
        }
        
    def _set_group(self):
        """
        Set default group parameters.
        """
        return {
            "name": U_ADMIN,
            "uuid": G_ADMIN,
            "desc": "Default administrator group",
            "protected": True   
        }
        
    def _set_user(self):
        """
        Set default user parameters.
        """
        return {
            "username": U_ADMIN,
            "group": G_ADMIN,
            "email": None,
            "password": None
        }
        
    def _set_utils(self):
        """
        Set default utility parameters
        """
        
        # Set the utility modules
        mod_gateway = 'cloudscape.engine.api.app.gateway.utils'
        mod_group   = 'cloudscape.engine.api.app.group.utils'
        mod_user    = 'cloudscape.engine.api.app.user.utils'
        
        # Return the database parameters
        return {
            "GatewayTokenGet": {
                "path": "gateway/token",
                "method": HTTP_GET,
                "desc": "Make a token request to the API gateway",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLGet": {
                "path": "gateway/acl",
                "method": HTTP_GET,
                "desc": "Retrieve an ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLCreate": {
                "path": "gateway/acl",
                "method": HTTP_POST,
                "desc": "Create a new ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLDelete": {
                "path": "gateway/acl",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLUpdate": {
                "path": "gateway/acl",
                "method": HTTP_PUT,
                "desc": "Update an existing ACL definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLObjectsGet": {
                "path": "gateway/acl/objects",
                "method": HTTP_GET,
                "desc": "Get a listing of ACL objects",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLObjectsUpdate": {
                "path": "gateway/acl/objects",
                "method": HTTP_PUT,
                "desc": "Update an ACL object definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLObjectsCreate": {
                "path": "gateway/acl/objects",
                "method": HTTP_POST,
                "desc": "Create a new ACL object definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayACLObjectsDelete": {
                "path": "gateway/acl/objects",
                "method": HTTP_DELETE,
                "desc": "Delete an existing ACL object definition",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayUtilitiesGet": {
                "path": "gateway/utilities",
                "method": HTTP_GET,
                "desc": "Get a listing of API utilities",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayUtilitiesOpen": {
                "path": "gateway/utilities/open",
                "method": HTTP_PUT,
                "desc": "Open an API utility for editing",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayUtilitiesClose": {
                "path": "gateway/utilities/close",
                "method": HTTP_PUT,
                "desc": "Close the editing lock on an API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayUtilitiesValidate": {
                "path": "gateway/utilities/validate",
                "method": HTTP_PUT,
                "desc": "Validate changes to an API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayUtilitiesSave": {
                "path": "gateway/utilities",
                "method": HTTP_PUT,
                "desc": "Save changes to an API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayUtilitiesCreate": {
                "path": "gateway/utilities",
                "method": HTTP_POST,
                "desc": "Create a new API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GatewayUtilitiesDelete": {
                "path": "gateway/utilities",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API utility",
                "mod": mod_gateway,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GroupMemberRemove": {
                "path": "group/member",
                "method": HTTP_DELETE,
                "desc": "Remove a user from an API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GroupMemberAdd": {
                "path": "group/member",
                "method": HTTP_POST,
                "desc": "Add a user to an API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GroupUpdate": {
                "path": "group",
                "method": HTTP_PUT,
                "desc": "Update an existing API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GroupCreate": {
                "path": "group",
                "method": HTTP_POST,
                "desc": "Create a new API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GroupDelete": {
                "path": "group",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "GroupGet": {
                "path": "group",
                "method": HTTP_GET,
                "desc": "Get details for an API group",
                "mod": mod_group,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "UserEnable": {
                "path": "user/enable",
                "method": HTTP_PUT,
                "desc": "Enable a user account",
                "mod": mod_user,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "UserDisable": {
                "path": "user/disable",
                "method": HTTP_PUT,
                "desc": "Disable a user account",
                "mod": mod_user,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "UserResetPassword": {
                "path": "user/pwreset",
                "method": HTTP_PUT,
                "desc": "Reset a user's password",
                "mod": mod_user,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "UserDelete": {
                "path": "user",
                "method": HTTP_DELETE,
                "desc": "Delete an existing API user",
                "mod": mod_user,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "UserCreate": {
                "path": "user",
                "method": HTTP_POST,
                "desc": "Create a new API user",
                "mod": mod_user,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            },
            "UserGet": {
                "path": "user",
                "method": HTTP_GET,
                "desc": "Get API user details",
                "mod": mod_user,
                "protected": True,
                "enabled": True,
                "object": "",
                "object_key": ""
            }
        }
        
    def get_input(self, k, d=None):
        """
        Retrieve the value of a user-defined (or default) input prompt
        """
        if k in self.input:
            return d if not self.input[k]['value'] else self.input[k]['value']
        return None
        
    def _set_input(self):
        """
        Set command input parameters
        """
        return {
            "db_host": {
                "type": "str",
                "default": "localhost",
                "prompt": "Please enter the hostname or IP address of the MySQL database server (localhost): ",
                "value": None
            },
            "db_port": {
                "type": "str",
                "default": "3306",
                "prompt": "Please enter the port to connect to the MySQL database server (3306): ",
                "value": None
            },
            "db_name": {
                "type": "str",
                "default": "cloudscape",
                "prompt": "Please enter the name of the database to use/create for Cloudscape (cloudscape): ",
                "value": None
            },
            "db_user": {
                "type": "str",
                "default": "cloudscape",
                "prompt": "Please enter the name of the primary non-root database user (cloudscape): ",
                "value": None
            },
            "db_password": {
                "type": "pass",
                "default": None,
                "prompt": "Please enter the password for the primary non-root database user: ",
                "value": None
            },
            "db_root_password": {
                "type": "pass",
                "default": None,
                "prompt": "Please enter the root password for the database server: ",
                "value": None
            },
            "api_admin_password": {
                "type": "pass",
                "default": None,
                "prompt": "Please enter a password for the default administrator account: ",
                "value": None
            },
            "api_admin_email": {
                "type": "str",
                "default": None,
                "prompt": "Please enter the email address for the default administrator account: ",
                "value": None
            },
            "api_host": {
                "type": "str",
                "default": "localhost",
                "prompt": "Please enter the hostname for the API server",
                "value": None
            },
            "api_port": {
                "type": "str",
                "default": "10550",
                "prompt": "Please enter the port for the API server",
                "value": None
            },
            "portal_host": {
                "type": "str",
                "default": "localhost",
                "prompt": "Please enter the hostname for the portal server",
                "value": None
            },
            "portal_port": {
                "type": "str",
                "default": "10550",
                "prompt": "Please enter the port for the portal server",
                "value": None
            },
            "socket_host": {
                "type": "str",
                "default": "localhost",
                "prompt": "Please enter the hostname for the socket server",
                "value": None
            },
            "socket_port": {
                "type": "str",
                "default": "10551",
                "prompt": "Please enter the port for the socket server",
                "value": None
            },
            "socket_bind_ipaddr": {
                "type": "str",
                "default": "localhost",
                "prompt": "Please enter the bind IP address for the portal server",
                "value": None
            }
        }