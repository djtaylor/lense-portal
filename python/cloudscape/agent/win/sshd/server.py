import os
import sys
import time
import Queue
import base64
import socket
import struct
import select
import paramiko
import threading
import pythoncom
from paramiko.message import Message

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common.vars import C_HOME, SSH_AUTHKEYS, SSH_HOSTKEY, SSH_DIR
from cloudscape.agent.common.config import AgentConfig
from cloudscape.agent.win.base import AgentHandler
from cloudscape.agent.win.sshd.scp import SCPInterface
from cloudscape.agent.win.sshd.terminal import WinTerminal

# Agent configuration and logger
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.win.sshd', CONFIG.log.sshd)

"""
SSH Server Interface

Interface class used to interact with the Paramiko SSH server module. Handles authentication,
PTY and shell requests, and other back-end stuff used to talk with native OpenSSH clients
on Linux machines, as well as the Paramiko SSH client libraries.
"""
class SSHInterface(paramiko.ServerInterface):
    
    # Class constructor
    def __init__(self, authkeys):
        self.event    = threading.Event()

        # Authorized public keys
        self.authkeys = authkeys

        # Session request type
        self.request  = None
        
    """ Request Handler """
    def get_request(self):
        return self.request
        
    """ SSH Channel Request """
    def check_channel_request(self, kind, chanid):
        LOG.info('Received channel request of type: %s' % kind)
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        
    """ Public Key Authentication """
    def check_auth_publickey(self, username, key):
        LOG.info('Client attempting public key authentication')
        
        # Validate the username and check if the key exists in 'authorized_keys'
        if username == 'cloudscape':
            for authkey in self.authkeys:
                if key == authkey: 
                    return paramiko.AUTH_SUCCESSFUL
                
        # Either wrong username or key
        return paramiko.AUTH_FAILED

    """ Interactive Authentication """
    def check_auth_interactive(self, username):
        LOG.error('Client attempted interactive authentication - not supported')
        return paramiko.AUTH_FAILED

    """ Password Authentication """
    def check_auth_password(self, username, password):
        LOG.error('Client attempted password authentication - not supported')
        return paramiko.AUTH_FAILED

    """ Enabled Authentication Mechanisms """
    def get_allowed_auths(self, username):
        return 'publickey'

    """ Check Exec Request """
    def check_channel_exec_request(self, channel, command):
        command = command if command.strip() else 'keepalive'
        
        # Set the request and event flags
        self.request = { 'type': 'exec', 'command': command }
        self.event.set()
    
        # Log and return true
        LOG.info('Client sent exec request: %s' % command)
        return True

    """ Channel Shell Request """
    def check_channel_shell_request(self, channel):
        LOG.info('Client requested shell')
        return True

    """ Channel PTY Request """
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        
        # Set the request and event flags
        self.request = { 'type': 'terminal' }
        self.event.set()
        
        # Log and return true
        LOG.info('Client requested terminal: type = %s, width = %s, height = %s, pxwidth = %s, pxheight = %s' % (term, width, height, pixelwidth, pixelheight))
        return True
    
"""
SSH Server Handler

Handler class that bootstraps the Python-SSHD server. Used for remote interactions with
the underlying Windows machine without needing to open an RDP session. Allows automation
and scripting from an platform that has an SSH client.

@todo    Need a better way to manage channel/transport/connection objects
@todo    Need to be able to handle multiple connections/requests over the same transport.
@todo    Automatic cleanup of inactive transports
"""
class SSHHandler(object):
    def __init__(self):
        
        # Authorized SSH keys
        self.authkeys    = self._load_auth_keys()
        
        # Client channels/transports/connections
        self.channels    = {}
        self.transports  = {}
        self.connections = {}
        
        # Server inputs, outputs, and message queue
        self.s_input     = []
        self.s_output    = []
        self.s_mqueues   = {}
        
        # Server address string
        self.addr_str    = '*' if not CONFIG.ssh.address else CONFIG.ssh.address
        
        # SSH socket and server objects
        self.sock        = None
        self.server      = None
    
        # Make sure the host keys are set
        self._set_host_keys()
    
        # Set Paramiko logger
        paramiko.util.get_logger('cloudscape.agent.win.sshd')
    
    """ Decode Base64 Public Key """
    def _decode_pubkey(self, key64):
        keydata = base64.b64decode(key64)
        parts = []
        while keydata:
            dlen = struct.unpack('>I', keydata[:4])[0]
            data,keydata = keydata[4:dlen+4], keydata[4+dlen:]
            parts.append(data)
        e_val = eval('0x' + ''.join(['%02X' % struct.unpack('B', x)[0] for x in parts[1]]))
        n_val = eval('0x' + ''.join(['%02X' % struct.unpack('B', x)[0] for x in parts[2]]))
        return parts[0],e_val,n_val
    
    """ Set Host Keys """
    def _set_host_keys(self):
        private_file = SSH_HOSTKEY
        public_file  = '%s.pub' % SSH_HOSTKEY
    
        # Make sure the SSH directory exists
        if not os.path.isdir(SSH_DIR):
            os.mkdir(SSH_DIR)
    
        # Generate a new keypair
        if not os.path.isfile(private_file) and not os.path.isfile(public_file):
            LOG.info('Generating host public/private key pair...')
            private_key = paramiko.RSAKey.generate(2048)
            public_key  = 'ssh-rsa %s cloudscape-windows-agent' % private_key.get_base64()
            
            # Write the private key
            LOG.info('Writing private host key: %s' % private_file)
            private_key.write_private_key_file(filename=private_file)
            
            # Write the public key
            LOG.info('Writing public host key: %s' % public_file)
            open(public_file, 'w').write(public_key)
    
    """ Reload Server """
    def _reload(self):
        if os.path.isfile('%s\\.sshd_reload' % C_HOME):
            global CONFIG
            
            # Reload server configuration
            CONFIG = AgentConfig().get()
            LOG.info('Reloading SSH server: configuration')
            
            # Reload authorized keys
            self.authkeys = self._load_auth_keys()
            LOG.info('Reloading SSH server: \'authorized_keys\'')
            
            # Remove the reload file marker
            os.unlink('%s\\.sshd_reload' % C_HOME)
    
    """ Remove Object """
    def _obj_remove(self, obj, target):
        try:
            if isinstance(target, list):
                target.remove(obj)
            if isinstance(target, dict):
                target.pop(obj, None)
        except:
            pass
    
    """ Load Authorized Keys """
    def _load_auth_keys(self):
        if not os.path.isfile(SSH_AUTHKEYS):
            raise Exception('Missing \'authorized_keys\' file: %s' % SSH_AUTHKEYS)
    
        # Read each public key
        authkeys = []
        with open(SSH_AUTHKEYS) as keys:
            for key in keys:
                
                # Grab the key contents
                b64_key = key.split(None)[1]
                
                # Extract the required key integers
                t,e,n = self._decode_pubkey(b64_key)
                
                # Construct the new SSH key message for Paramiko
                key_msg = Message()
                key_msg.add_string(t)
                key_msg.add_mpint(e)
                key_msg.add_mpint(n)
                key_msg.rewind()
                
                # Create the RSA key object and append to the authorized keys array
                authkeys.append(paramiko.RSAKey(msg=key_msg))
        return authkeys
    
    """ Send Status and Close """
    def _send_status_and_close(self, ck, msg=None, status=0):
        try:
            if msg:
                self.channels[ck].sendall('\x01ssh: ')
                self.channels[ck].sendall(str(msg))
                self.channels[ck].sendall('\n')
            self.channels[ck].send_exit_status(status)
        except socket.error, ex:
            LOG.warn('Failed to properly close the channel: %r' % ex.message)
        finally:
            try:
                self._clear_connection(ck)
            except socket.error:
                pass
    
    """ Handle SCP Requests """
    def _scp_handle(self, ck, connection, cmd, client_address):
        pythoncom.CoInitialize()
        SCPInterface(self.channels[ck], connection).run(cmd, client_address)
        try:
            self._clear_connection(ck)
        except:
            pass
    
    """ Handle Agent Requests """
    def _agent_handle(self, ck, cmd):
        pythoncom.CoInitialize()
        args = cmd.split()
        args.pop(0)
        msg, code = AgentHandler(args=args, term=True).main()
        self.channels[ck].sendall(str(msg))
        self._send_status_and_close(ck, status=code)
    
    """ Start Terminal Thread """
    def _start_term(self, ck):
        pythoncom.CoInitialize()
        term = WinTerminal()
        term.start(self.channels[ck], self.connections[ck])
        LOG.info('Closing terminal session for client: [%s]' % ck)
        self._send_status_and_close(ck)
    
    """ Close Transports """
    def _close_transports(self):
        for ck, ct in self.transports.iteritems():
            if (hasattr(ct, 'close')) and (callable(getattr(ct, 'close'))):
                LOG.info('Closing client transport: [%s]' % ck)
                ct.close()
    
    """ Close Channels """
    def _close_channels(self):
        for ck, cc in self.channels.iteritems():
            if (hasattr(cc, 'close')) and (callable(getattr(cc, 'close'))):
                LOG.info('Closing client channel: [%s]' % ck)
                cc.close()
    
    """ Open Channel """
    def _open_channel(self, ck):
        self.channels[ck] = self.transports[ck].accept(20)
    
        # If no channel was created
        if self.channels[ck] is None:
            LOG.error('Failed to create client channel for: [%s]' % ck)
            self._obj_remove(ck, self.channels)
            self._obj_remove(ck, self.transports)
            return
        self.channels[ck].setblocking(0)
        LOG.info('Client successfully authenticated')
    
    """ Bind Socket """
    def _bind_socket(self):
    
         # Bind to the SSH port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set the socket to non-blocking and bind to the address and port
            self.sock.setblocking(0)
            self.sock.settimeout(10)
            self.sock.bind((CONFIG.ssh.address, CONFIG.ssh.port))
            
        # Failed to bind the server
        except Exception as e:
            LOG.error('Failed to bind SSH server to [%s:%s]: %s' % (self.addr_str, CONFIG.ssh.port, str(e)))
            sys.exit(1)
    
    """ Listen Socket """
    def _listen_socket(self):
    
        # Listen for incoming connection
        try:
            self.sock.listen(100)
            
            # Add the socket object to the inputs array
            self.s_input.append(self.sock)
        
        # Failed to start the listener
        except Exception as e:
            LOG.exception('Failed to listen for connections: %s' % str(e))
            sys.exit(1)
    
    """ Initialize Socket """
    def _init_socket(self):
    
        # Bind the socket
        self._bind_socket()
        LOG.info('Binding SSH server to [%s:%s]' % (self.addr_str, CONFIG.ssh.port))
            
        # Listen for connections
        self._listen_socket()
        LOG.info('Started SSH server, listening for connections on port %s' % (CONFIG.ssh.port))
    
    """ Set Connection Objects """
    def _set_connection(self, ck, conn):
        self.connections[ck] = conn
        self.s_input.append(conn)
        self.s_mqueues[conn] = Queue.Queue()
    
    """ Clear Connection Objects """
    def _clear_connection(self, ck):
        
        # Delete from select input and message queues
        self._obj_remove(self.connections[ck], self.s_input)
        self._obj_remove(self.connections[ck], self.s_mqueues)
        
        # Close out the channel
        try:
            self.channels[ck].close()
            time.sleep(1)
            self.transports[ck].close()
            self.connections[ck].close()
        except:
            pass
        
        # Delete the old channel
        self._obj_remove(ck, self.channels)
        self._obj_remove(ck, self.transports)
        self._obj_remove(ck, self.connections)
    
    """ Connection Handler """
    def _connect_handler(self):
        try:
            while self.s_input:
                time.sleep(1)
                
                # Break if halting the server
                if self.proc['halt']: break
                
                # Get receive/write/exceptions
                s_r, s_w, s_e = select.select(self.s_input, self.s_output, self.s_input, 1)
            
                # Stuff to do while the server is running in the background
                if not (s_r or s_w or s_e):
                    self.proc_check_halt()
                    self._reload()
            
                # Handle inputs
                for s in s_r:
                    
                    # Close off the channel and remove input/output queues after the session is done
                    if not s is self.sock:
                        self._obj_remove(s, self.s_output)
                        self._obj_remove(s, self.s_input)
                        self._obj_remove(s, self.s_mqueues)
                        
                    # Handle starting the session and session data
                    else:
                        
                        # Accept client connections
                        connection, client_address = s.accept()
                        LOG.info('Received connection from: [%s:%s]' % (client_address[0], client_address[1]))
                        
                        # Set the connection to non-blocking
                        connection.setblocking(0)
                        
                        # Client key
                        ck = '%s:%s' % (client_address[0], client_address[1])
                        
                        # Try to negotiate the session
                        try:
                            self.transports[ck] = paramiko.Transport(connection)
                            try:
                                self.transports[ck].load_server_moduli()
                            except:
                                LOG.warn('Failed to load server module - GEX will be unsupported')
                                raise
                            
                            # Add the server host key
                            self.transports[ck].add_server_key(paramiko.RSAKey(filename=SSH_HOSTKEY))
                            
                            # Create the SSH server interface
                            self.server = SSHInterface(self.authkeys)
                            
                            # Try to start the authenticate SSH session
                            try:
                                self.transports[ck].start_server(server=self.server)
                            except paramiko.SSHException:
                                LOG.error('SSH negotation failed')
                                sys.exit(1)
                                
                            # Open a new channel
                            self._open_channel(ck)
                            
                            # Wait for a request event
                            self.server.event.wait(10)
                            request = self.server.get_request()
                            if not (request) or not ('type' in request):
                                LOG.warn('[%s]: Missing request object or request["type"] parameter' % ck)
                                return
                            
                            # Daemonized Terminal Thread
                            if request['type'] == 'terminal':
                                
                                # Connection is valid, append to server objects
                                self._set_connection(ck, connection)
                                
                                # Create a new terminal thread
                                tt = threading.Thread(target=self._start_term, args=[ck], name=ck)
                                tt.setDaemon(True)
                                tt.start()
                                LOG.info('Started client terminal thread: [%s]' % ck)
                                
                            # Exec Request [SCP/Agent]
                            exec_types = ['scp', 'agent', 'keepalive']
                            if request['type'] == 'exec':
                                try:
                                    root = request['command'].split()[0]
                                    if not root in exec_types:
                                        self._send_status_and_close(ck, msg='Command not supported', status=1)
                                    self._set_connection(ck, connection)
                                        
                                    # Keepalive
                                    if root == 'keepalive':
                                        self._send_status_and_close(ck, status=0)
                                        
                                    # SCP [Send/Receive Files]
                                    if root == 'scp':
                                        st = threading.Thread(target=self._scp_handle, args=[ck, connection, request['command'], client_address], name=ck)
                                        st.setDaemon(True)
                                        st.start()
                                        LOG.info('Started client SCP thread: [%s]' % ck)
                                        
                                    # Agent [Run Agent Command]
                                    if root == 'agent':
                                        at = threading.Thread(target=self._agent_handle, args=[ck, request['command']], name=ck)
                                        at.setDaemon(True)
                                        at.start()
                                        LOG.info('Started client agent thread: [%s]' % ck)
                                        
                                # Error when running exec request
                                except Exception as e:
                                    LOG.exception('Encountered exception when processing exec request: %s' % str(e))
                                    self._send_status_and_close(ck, 'Internal error', 1)
                        
                        # Error in session negotiation
                        except Exception as e:
                            LOG.exception('Caught exception in SSH client connection: %s' % str(e))
                            try:
                                self.transports[ck].close()
                            except:
                                pass
        
        # Socket exception
        except socket.error as e:
            LOG.exception('Encountered fatal socket error: %s' % e.strerror)
            sys.exit(1)

        # Keyboard interrupts when debugging
        except KeyboardInterrupt:
            LOG.info('Receiving interrupt signal - exiting...')
            try:
                self._close_transports()
            except:
                pass
            sys.exit(0)
    
    """ Stop Server """
    def stop(self):
        LOG.info('Shutting down CloudScape SSH server...')
        try:
            
            # Close all channels and transports
            self._close_channels()
            self._close_transports()
            
            # Close the socket
            self.sock.close()
        except Exception as e:
            LOG.warn('Close channel/transport/sockets: ' % e.message)
    
    """ Start Server """
    def start(self):
        
        # Set the halt method to be called when the halt flag is set to true
        self.proc_set_halt(self.stop)
        
        # Initialize the socket
        self._init_socket()
            
        # Begin handling incoming connections
        self._connect_handler()