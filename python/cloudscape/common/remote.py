import os
import re
import copy
import paramiko
import StringIO
import unicodedata
from paramiko import SSHException, BadHostKeyException

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.common.scp import SCPClient
from cloudscape.common.utils import valid, invalid

class RemoteConnect(object):
    """ 
    Wapper class designed to handle remote SSH connections to both Linux
    and Windows hosts. Provides methods to open a connection, run remote
    commands, as well as basic SCP functionality.
    
    The connection object can use either password or SSH key authentication
    to connect to the remote host.
    
    Setting up a connection::
    
        # Import the class
        from cloudscape.common.remote import RemoteConnect
        
        # SSH password connection parameters. Note that 'port' is optional for
        # both password and key authentication and defaults to 22.
        pass_params = {
            'host': '192.168.0.12',
            'user': 'admin',
            'password': 'secret',
            'port': 22
        }
        
        # SSH key connection parameters. The key parameter can either be a path
        # to a file, or a private key you have read into a string.
        key_params = {
            'host': '192.168.0.12',
            'user': 'admin',
            'key': '/home/user/.ssh/private_key'
        }
        
        # Setup the connection
        remote = RemoteConnect('linux', key_params)
    """
    def __init__(self, sys_type='linux', conn={}):
        
        """
        Initialize a Paramiko SSH connection.

        :param sys_type: The type of machine to connection, either 'linux' or 'windows'. Defaults to 'linux'
        :type  sys_type: str 
        :param conn:     SSH connection parameters.
        :type  conn:     dict
        """
        
        self.conf = config.parse()
        self.log  = logger.create(__name__, self.conf.server.log)
        
        # Valid system types
        self.sys_types    = ['linux', 'windows']
        
        # Required connection parameters
        self.conn_attr    = {
            'linux':   ['host', 'user'],
            'windows': ['host', 'user']
        }
        
        # Remote system type and connection parameters
        self.sys_type     = sys_type
        self.sys_conn     = copy.copy(conn)
        
        # Make sure connection parameters are valid
        self.params_valid = self._validate()
        
        # Set any default connection parameters
        if self.params_valid['valid'] == True:
            self._set_defaults()
    
    """ ERROR MESSAGES
    
    Method to define string messages for internal error codes.
    """
    def _error(self, code):
        
        # Error code numbers and messages
        error_codes = {
            000: "Missing required 'type' parameter",
            001: "Unsupported 'type' parameter '%s' - must be one of '%s'" % (self.sys_type, str(self.sys_types)),
            002: "Missing required 'conn' paremeter for remote connection details",
            003: "Remote commands must be in list format",
            004: "Files argument must be in list format",
            005: "Cannot use sudo on host '%s', no password provided'" % self.sys_conn['host'],
            100: "Must supply a 'passwd' or 'key' connection parameter for system type '%s'" % (self.sys_type),
            101: "Missing a required connection parameter for system type '%s', must supply '%s'" % (self.sys_type, str(self.conn_attr[self.sys_type])),
            999: "An unknown error occured when creating the remote connection"
        }
        
        # Return the error message
        if not code or not code in error_codes:
            return error_codes[999]
        else:
            return error_codes[code]
        
    """ SET DEFAULTS
    
    Set any defaults for unspecific, optional connection parameters depending
    on the system type.
    """
    def _set_defaults(self):
        
        # System Defaults
        if not 'port' in self.sys_conn or not self.sys_conn['port']:
            self.sys_conn['port'] = 22

    """ LOAD SSH KEY
    
    Method to load an SSH key for a Linux connection into a Parmiko object.
    """
    def _load_ssh_key(self):
        if os.path.isfile(self.sys_conn['key']):
            key_obj = paramiko.RSAKey.from_private_key_file(self.sys_conn['key'])
        else:
            key_str = unicodedata.normalize('NFKD', self.sys_conn['key']).encode('ascii', 'ignore')
            key_fo  = StringIO.StringIO(key_str)
            key_obj = paramiko.RSAKey.from_private_key(key_fo)
        return key_obj

    """ VALIDATE PARAMETERS
    
    Make sure the system type and connection parameters are valid. Check the
    connection parameters based on the system type.
    """
    def _validate(self):
        
        # Require a system type parameter
        if not self.sys_type: 
            return invalid(self._error(000))
        
        # Make sure the system type is supported
        if not self.sys_type in self.sys_types:
            return invalid(self._error(001))
            
        # Require system connection parameters
        if not self.sys_conn or not isinstance(self.sys_conn, dict):
            return invalid(self._error(002))
            
        # Windows system type validation
        if self.sys_type == 'windows':
            
            # Require an SSH key
            if not 'key' in self.sys_conn:
                return invalid(self._error(100))
            
        # Linux system type validation
        if self.sys_type == 'linux':
            
            # Make sure either a key or password are set
            if not ('passwd' in self.sys_conn) and not ('key' in self.sys_conn):
                return invalid(self._error(100))
            
        # Make sure the required parameters are set
        for param in self.conn_attr[self.sys_type]:
            if not param in self.sys_conn:
                return invalid(self._error(101))
            
        # If a key is specified, read into an RSA object
        if 'key' in self.sys_conn and self.sys_conn['key']: 
            self.auth_type       = 'key'
            self.sys_conn['key'] = self._load_ssh_key()
        else:
            self.auth_type       = 'passwd'
            self.sys_conn['key'] = None
                
        # Connection parameters OK
        return valid()
      
    """ Connection Handler """
    def _connect(self):
        try:
            if self.auth_type == 'key':
                self.client_exec.connect(self.sys_conn['host'], 
                    username = self.sys_conn['user'], 
                    port     = int(self.sys_conn['port']), 
                    pkey     = self.sys_conn['key'])
            else:
                self.client_exec.connect(self.sys_conn['host'], 
                    username = self.sys_conn['user'], 
                    port     = int(self.sys_conn['port']), 
                    password = self.sys_conn['passwd'])
        except BadHostKeyException as e:
            self.log.exception('Failed to establish SSH connection: %s' % str(e))
            return invalid(str(e))
        
        # Open the SCP client
        self.client_copy = SCPClient(self.client_exec.get_transport())
        return valid()
        
    def open(self):
        """
        Open the connection to the remote host with the constructed connection
        object. This class is called internally to the API, so the return object
        is constructed accordingly. 
        
        The open method returns a dictionary with two
        elements, 'valid' and 'content'. If the connection failed, 'valid' is set
        to False and 'content' contains the error. Otherwise, 'valid' is set to True.
        
        :rtype: dictionary
        
        Opening a connection::
            
            # Attempt to connect
            status = remote.open()
        
            # If the connection failed to open
            if not status['valid']:
        
                # You can return the object to the calling module or raise your own Exception
                return status
        """
        
        # Make sure connection parameters are valid
        if not self.params_valid['valid']:
            self.log.error(self.params_valid['content'])
            return invalid(self.params_valid['content'])
            
        # Remote command and file copy clients
        self.client_exec = None
        self.client_copy = None
            
        # Set the client for remote commands
        self.client_exec = paramiko.SSHClient()
        self.client_exec.load_system_host_keys()
        self.client_exec.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Try to establish the parent SSH connection
        try:
            auth_type = 'key' if (self.auth_type == 'key') else 'password'
            self.log.info('Attempting %s authentication to \'%s@%s\'' % (auth_type, self.sys_conn['user'], self.sys_conn['host']))
            conn_status = self._connect()
            if not conn_status['valid']:
                return conn_status
            self.log.info('Successfully established connection to \'%s@%s\'' % (self.sys_conn['user'], self.sys_conn['host']))
        
        # Failed to establish SSH connection
        except Exception as e:
            return invalid(self.log.exception('SSH connection to \'%s@%s\' failed with error: %s' % (self.sys_conn['user'], self.sys_conn['host'], e)))
        
        # Return the connection object
        return valid(self)
  
    def close(self):
        """
        Close the connection once you have finished running commands and copying
        files. Ends interaction with the remote host.
        
        If there is a problem with closing the connection, an exception will be
        logged, but the program will continue as normal.
        
        Closing a connection::
            
            # Attempt to close the connection
            remote.close()
        """
        
        try:
            self.client_exec.close()
            self.log.info('Closed all remote connections to host \'%s\'' % (self.sys_conn['host']))
        except Exception as e:
            self.log.exception('Failed to close all remote connections to host \'%s\': %s' % (self.sys_conn['host'], str(e)))

    def execute(self, commands=[]):
        """
        Run a series of remote commands on the server. Takes a single argument,
        which is a list of commands to run. The exit code, stdout, and stderr
        are captured for each command and returned in a list.
        
        If any commands fail to run, this is logged and the rest of the commands
        continue as normal.
        
        :param  commands: A list of commands to run on the remote server
        :type   commands: list
        :rtype: list of dictionaries
        
        Running commands::
            
            # A list of commands to run
            commands = ['uname', 'hostname']
            
            # Run the commands and capture the output
            output = remote.execute(commands)
        
        Example output structure::
        
            output = [
                {
                    'command': 'uname',
                    'exit_code': 0,
                    'stdout': ['Linux cloudscape 3.8.0-29-generic #42~precise1-Ubuntu SMP Wed Aug 14 16:19:23 UTC 2013 x86_64 x86_64 x86_64 GNU/Linux'],
                    'stderr': []
                },
                {
                    'command': 'hostname',
                    'exit_code': 0,
                    'stdout': ['myserver'],
                    'stderr': []
                }
            ]
        """
        if not commands or not isinstance(commands, list):
            self.log.error(self._error(003))
            return invalid(self._error(003))
        self.log.info('Preparing to run [%s] commands on [%s] host' % (len(commands), self.sys_type))
        
        # Windows remote commands
        if self.sys_type == 'windows':
            
            # Variable to store stdout and stderr
            output = []
            
            # Run each command in the list
            for command in commands:
                tried = False
                def win_ssh_exec(command, false):
                    try:
                        stdin, stdout, stderr = self.client_exec.exec_command(command)
                        
                        # Get the exit code
                        exit_code = stdout.channel.recv_exit_status()
            
                        # Save the command output
                        self.log.info('Ran command \'%s\' on host \'%s\' with exit code \'%s\'' % (command, self.sys_conn['host'], exit_code))
                        output.append({'command': command,
                                       'exit_code': exit_code,
                                       'stdout': stdout.readlines(), 
                                       'stderr': stderr.readlines()})
                        return True
                       
                    # Need to reconnect
                    except Exception as e:
                        if not tried:
                            conn_status = self._connect()
                            if not conn_status['valid']:
                                self.log.error('Lost connection while running command: [%s]' % command)
                                return False
                            win_ssh_exec(command, tried)
                        else:
                            self.log.exception('Failed to run command \'%s\' on host \'%s\' with error: %s' % (command, self.sys_conn['host'], str(e)))
                        
                # Windows SSH exec wrapper
                win_ssh_exec(command, tried)
            return output
        
        # Linux remote commands
        if self.sys_type == 'linux':
            
            # Variable to store stdout and stderr
            output = []
            
            # Run each command in the list
            for command in commands:
                try:
                    
                    # Sudo Metacharacter
                    #
                    # Allow an API call with the {%sudo%} special metacharacter. If running with
                    # a non-root user, and a password is available, extract the command and try to
                    # run with sudo privileges.
                    if re.match(r'^{sudo}.*$', command):
                        command = re.compile('^{sudo}(.*$)').sub(r'\g<1>', command)
                        if self.sys_conn['user'] != 'root':
                            if not self.sys_conn['passwd']:
                                self.log.error(self._error(005))
                                continue
                            else:
                                sudo        = True
                                sudo_passwd = self.sys_conn['passwd']
                        else:
                            sudo = False
                    else:
                        sudo = False
                    
                    # Optional sudo password for non-root accounts
                    if sudo:
                        cmd_string = 'sudo -S bash -l -c \'%s\'' % command
                        stdin, stdout, stderr = self.client_exec.exec_command(cmd_string)
                        stdin.write('%s\n' % sudo_passwd)
                        stdin.flush()
                    
                    # Non-root commands
                    else:
                        cmd_string = 'bash -l -c \'%s\'' % command
                        stdin, stdout, stderr = self.client_exec.exec_command(cmd_string)
                        
                    # Get the exit code
                    exit_code = stdout.channel.recv_exit_status()
                        
                    # Save the command output
                    self.log.info('Ran command \'%s\' on host \'%s\' with exit code \'%s\'' % (cmd_string, self.sys_conn['host'], exit_code))
                    output.append({'command': command,
                                   'exit_code': exit_code,
                                   'stdout': stdout.readlines(), 
                                   'stderr': stderr.readlines()})
                    
                # Failed to execute remote command
                except Exception as e:
                    self.log.error('Failed to run command \'%s\' on host \'%s\' with error: %s' % (command, self.sys_conn['host'], e))
            return output
        
    def chmod(self, path=None, mode=None, file_mode=None, dir_mode=None, recurse=False):
        """
        Change permissions of a file or directory on the remote server. Currently
        only supported for Linux because right now I'm too lazy to abstract the
        differences for Windows permissions.
        
        This method uses the 'execute' method to run these commands.
        
        :param  path: The file or directory you want to modify
        :type   path: str
        :param  mode: The octal permissions to set (for a single file or all contents)
        :type   mode: str
        :param  file_mode: If modifying a directory, mode to apply to files
        :type   file_mode: str
        :param  dir_mode: If modifying a directory, mode to apply to folders
        :type   file_mode: str
        :param  recurse: Whether or not to recurse into subdirectories
        :type   recurse: bool
        
        Changing permissions::
            
            # Change permissions of a single file
            remote.chmod(path='/tmp/somefile.txt', mode='755')
            
            # Change permissions on only files recursively
            remote.chmod('/tmp/somepath', file_mode='644', recurse=True)
            
            # Change permissions on both files and folders recursively
            remote.chmod('/tmp/someotherpath', file_mode='644', dir_mode='755', recurse=True)
        """
        if not path or not mode:
            return False
        
        # Only valid for Linux machines
        if self.sys_type == 'linux':
        
            # Build the base command
            cmd_base = 'chmod -R' if recurse else 'chmod'
            
            # Global permissions
            if mode: 
                self.execute(['%s %s %s' % (cmd_base, mode, path)])
            
            # File permissions
            if file_mode:
                if recurse == True:
                    self.execute(['find %s -type f -exec chmod %s {} \;' % (path, file_mode)])
                else:
                    self.execute(['find %s -maxdepth 1 -type f -exec chmod %s {} \;' % (path, file_mode)])
                    
            # Directory permissions
            if dir_mode:
                if recurse == True:
                    self.execute(['find %s -type d -exec chmod %s {} \;' % (path, dir_mode)])
                else:
                    self.execute(['find %s -maxdepth 1 -type d -exec chmod %s {} \;' % (path, dir_mode)])
        
    def chown(self, path=None, user=None, group=None, recurse=False):
        """
        Change ownership of a file or directory structure. Optional flags
        to use a different name/group combination, and to recurse into the
        base path.
        
        This method uses the 'execute' method to run these commands.
        
        :param  path: The file or directory you want to modify
        :type   path: str
        :param  user: The user to change ownership to
        :type   user: str
        :param  group: The optional group to change ownership to
        :type   group: str
        :param  recurse: Whether or not to recurse into subdirectories
        :type   recurse: bool
        
        Changing ownership::
            
            # Set ownership on a single file
            remote.chown(path='/some/file.txt', user='name', group='name')
        
            # Set ownership recursively on an entire path
            remote.chown(path='/some/path', user='name', group='name', recurse=True)
        """
        if not path or not user:
            return False
        
        # Only valid for Linux machines
        if self.sys_type == 'linux':
        
            # Build the remote command
            cmd_base = 'chown -R' if recurse else 'chown'
            
            # Set the user/group string
            cmd_owner = user
            if group:
                cmd_owner = '%s:%s' % (user, group)
            
            # Set the owner of the path
            self.execute(['%s %s %s' % (cmd_base, cmd_owner, path)])

    def send_file(self, local=None, remote=None, mode=False, user=False, group=False):
        """
        Send a file to a remote server, and for Linux systems, optionally specify the
        remote file permissions to set after transfer.
        
        :param  local: The path to the local file to send
        :type   local: str
        :param  remote: The path to the remote file (defaults to local if not set)
        :type   remote: str
        :param  mode: The optional modal permissions
        :type   mode: str
        :param  user: The optional owner (user)
        :type   user: str
        :param  group: The optional owner (group)
        :type   group: str
        
        Sending a file::
            
            # Sending a file where the remote path matches the local path
            remote.send_file(local='/some/file.txt')
        
            # Sending a file to a different remote path
            remote.send_file(local='/some/file.txt', remote='/some/otherfile.txt')
        
            # Sending a file and setting permissions
            remote.send_file(local='/some/file.txt', mode=644, user='name', group='name')
        """
        if not self.client_copy:
            return False
        
        # Default destination to source path if none provided
        if not remote: remote = local
        
        # Send the file
        tried = False
        def try_send(local, remote, mode, user, group, tried):
            try:
                self.client_copy.put(local, remote)
                self.log.info('Copied file \'%s\' to remote server \'%s\':\'%s\'' % (local, self.sys_conn['host'], remote))
                
                # Additional Linux options
                if self.sys_type == 'linux':
                
                    # Optional file mode
                    if mode:
                        self.chmod(path=remote, mode=mode)
                            
                    # Optional file ownership
                    if user:
                        self.chown(path=remote, user=user, group=group, recurse=False)
                
            # Failed to send the file, try to reconnect and send again
            except Exception as e:
                if not tried:
                    conn_status = self._connect()
                    if not conn_status['valid']:
                        self.log.error('Lost connection while transferring file: [%s]' % local)
                        return False
                    tried = True
                    try_send(local, remote, mode, user, group, tried)
                else:
                    self.log.exception('Failed to send file \'%s\' to remote server \'%s\':\'%s\' with error: %s' % (local, self.sys_conn['host'], remote, e))
        
        # Launch the send wrapper
        try_send(local, remote, mode, user, group, tried)
            
    def get_file(self, remote=None, local=None):
        """
        Get a file from a remote server.
        
        :param  remote: The path on the remote server to retrieve
        :type   remote: str
        :param  local: The local path to transfer to (defaults to the same as remote)
        :type   local: str
        
        Getting a file::
            
            # Get a remote file and preserve the path
            remote.get_file(remote='/some/file.txt')
    
            # Get a remote file and use a new local path
            remote.get_file(remote='/some/file.txt', local='/some/otherfile.txt')
        """
        if not self.client_copy:
            return False
        
        # Default local path to remote path
        if not local: local = remote
        
        # Get the file
        tried = False
        def try_get(remote, local, tried):
            try:
                self.client_copy.get(remote, local)
                self.log.info('Retrieved file \'%s\' from remote server \'%s\':\'%s\'' % (local, self.sys_conn['host'], remote))
            except Exception as e:
                if not tried:
                    conn_status = self._connect()
                    if not conn_status['valid']:
                        self.log.error('Lost connection while retrieving file: [%s]' % remote)
                        return False
                    tried = True
                    try_get(remote, local, tried)
                else:
                    self.log.exception('Failed to get file \'%s\' from remote server \'%s\':\'%s\' with error: %s' % (local, self.sys_conn['host'], remote, e))
                
        # Launch the get wrapper
        try_get(remote, local, tried)