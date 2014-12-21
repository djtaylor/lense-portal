import os
import re
import stat
import socket
import ntpath
import traceback
import threading
from paramiko.message import Message
from paramiko.py3compat import byte_chr
from paramiko.buffered_pipe import BufferedPipe

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.agent.common.config import AgentConfig

""" SSH2 Response Codes

Pulled directly from the source code for the SFTP server in OpenSSH.
"""
SSH2_FXP_STATUS=101
SSH2_FX_OK=0
SSH2_FX_EOF=1
SSH2_FX_NO_SUCH_FILE=2
SSH2_FX_PERMISSION_DENIED=3
SSH2_FX_FAILURE=4
SSH2_FX_BAD_MESSAGE=5
SSH2_FX_NO_CONNECTION=6
SSH2_FX_CONNECTION_LOST=7
SSH2_FX_OP_UNSUPPORTED=8
SSH2_EXTENDED_DATA_STDERR=1
SSH2_MSG_CHANNEL_WINDOW_ADJUST=93
SSH2_MSG_CHANNEL_DATA=94
SSH2_MSG_CHANNEL_EXTENDED_DATA=95


""" SSH Response Message Constants

Used mainly for debugging.
"""
SCP_STATUS = {
    0: 'Success',
    1: 'End of file',
    2: 'File not found',
    3: 'Permission denied',
    4: 'Failure',
    5: 'Bad message',
    6: 'No connection',
    7: 'Connection lost',
    8: 'Operation unsupported'  
}

# Configuration and logger objects
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.win.scp', CONFIG.log.sshd)

""" SCP Exception """
class SCPException(Exception):
    def __init__(self, status, message):
        self.status = status
        super(Exception, self).__init__(message)

"""
SCP Server

Base class for the SCPInterface, used to handle sending and receiving data
from the SCP client.
"""
class SCPServer:
    
    # Chunk size, connect timeout, and ACK signal
    SCP_CHUNK_SIZE = 64*1024
    SCP_TIMEOUT    = 30.0
    SCP_ACK        = '\x00'
    SCP_WIN_ADJ    = byte_chr(SSH2_MSG_CHANNEL_WINDOW_ADJUST)
        
    # SCP command flags
    SCP_RECURSIVE  = '-r'
    SCP_RECEIVE    = '-t'
    SCP_SEND       = '-f'
        
    # Class constructor
    def __init__(self):
        self.buffer = ''
        self.out_buffer = BufferedPipe()
        
    """ Buffer Pointer
    
    Returns a pointer to the first used byte in the buffer
    """
    def _buffer_ptr(self, buffer):
        pass
        
    """ Send Extended Data Status """
    def send_ext_data(self, data):
        m = Message()
        m.add_byte(byte_chr(SSH2_MSG_CHANNEL_EXTENDED_DATA))
        m.add_int(self.channel.remote_chanid)
        m.add_int(SSH2_EXTENDED_DATA_STDERR)
        m.add_string(data)
        self.channel.transport._send_user_message(m)
        
    """ Send Window Adjust """
    def send_window_adjust(self, consumed):
        m = Message()
        m.add_byte(byte_chr(SSH2_MSG_CHANNEL_WINDOW_ADJUST))
        m.add_int(self.channel.remote_chanid)
        m.add_int(consumed)
        self.channel.transport._send_user_message(m)
        
    """ Send Status and Close """
    def send_status_and_close(self, msg=None, status=0):
        try:
            if msg:
                self.channel.sendall('\x01scp: ')
                self.channel.sendall(str(msg))
                self.channel.sendall('\n')
            self.channel.send_exit_status(status)
        except socket.error, ex:
            LOG.warn('Failed to properly close the channel: %r' % ex.message)
        finally:
            try:
                self.channel.close()
            except socket.error:
                pass
        
    """ Send File """
    def send(self):
        file_stat = os.stat(self.file)
        
        # Make sure the file exists
        if not os.path.isfile(self.file):
            LOG.error('Could not locate file: %s' % self.file)
            self.send_status_and_close(SCP_STATUS[SSH2_FX_NO_SUCH_FILE], SSH2_FX_NO_SUCH_FILE)
        
        # Make sure sending a regular file
        if not stat.S_ISREG(file_stat.st_mode):
            LOG.error('Cannot send a non-regular file: %s' % self.file)
            self.send_status_and_close('Not a regular file', SSH2_FX_NO_SUCH_FILE)
        file_modes = 'C%04o %i %s\n' % (file_stat.st_mode & 07777, file_stat.st_size, ntpath.basename(self.file))
        
        # Send the file
        self.send_ext_data('Sending file modes: %s' % file_modes)
        self.channel.sendall(file_modes)
        self.wait_for_ack()
        
        # Open the file and transmit contents
        try:
            fd   = open(self.file, 'rb')
            LOG.info('Opening file [%s] and sending contents' % self.file)
            size = file_stat.st_size
            bytes_sent = 0
            while bytes_sent < size:
                
                # Need to use a smaller chunk size for sending back to Linux SCP clients
                chunk = fd.read(16*1024)
                self.channel.send(chunk)
                bytes_sent += len(chunk)
                
            # End of transfer
            self.channel.send(self.SCP_ACK)
            self.wait_for_ack()
            LOG.info('File contents sent and acknowledged, closing connection' % self.file)
            self.channel.send_exit_status(0)
            
        # Failed to read or send file
        except IOError as e:
            if e.errno == 13:
                LOG.exception('Access to \'%s\' denied: %s' % (self.file, e.strerror))
                self.send_status_and_close(SCP_STATUS[SSH2_FX_PERMISSION_DENIED], SSH2_FX_PERMISSION_DENIED)
            else:
                LOG.exception('Failed to write file \'%s\': %s' % (self.file, e.strerror))
                self.send_status_and_close(SCP_STATUS[SSH2_FX_FAILURE], SSH2_FX_FAILURE)
        
        # Other exceptions
        except Exception as e:
            LOG.exception('Failed to send file \'%s\': %s' % (self.file, e.strerror))
            self.send_status_and_close('Internal error', SSH2_FX_FAILURE)
        
    """ Receive Buffer """
    def recv(self, size):
        if self.buffer:
            result = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return result
        return self.channel.recv(size)
        
    """ Receive Line """
    def recv_line(self):
        if '\n' not in self.buffer:
            while True:
                chunk = self.channel.recv(1024)
                self.buffer += chunk
                if '\n' in chunk:
                    break
                
        line, self.buffer = self.buffer.split('\n', 1)
        return line
        
    """ Receive File 
    
    Start the file transfer request from the remote server to the local host.
    """
    def receive(self): 
        self.channel.send(self.SCP_ACK)

        # Base directory doesn't exist
        if not os.path.isdir(self.path):
            LOG.error('Directory does not exist: %s' % self.path)
            self.send_status_and_close(SCP_STATUS[SSH2_FX_NO_SUCH_FILE], SSH2_FX_NO_SUCH_FILE)
    
        # Get the record for the file transfer
        record = self.recv_line()
        self.receive_inner(record)
        
    """ Receive Contents 
    
    Receive file contents. For now I am only going to support sending and receiving
    single files from the Windows server.
    """
    def receive_inner(self, record):
        mode, size, name = record[1:].split(' ', 2)
        
        # Get the size of the file
        try:
            size = int(size)
        except ValueError as e:
            LOG.exception('Could not retrieve size of file: %s' % e.strerror)
            self.send_status_and_close(SCP_STATUS[SSH2_FX_FAILURE], SSH2_FX_FAILURE)
        
        # Attempt to write to the file
        try:     
            fd = open(self.file, 'wb')
            LOG.info('Opening file [%s] and receiving contents' % self.file)
            
            # Send the ACK flag
            self.channel.send(self.SCP_ACK)
            
            # Start receiving the file
            bytes_sent = 0
            file_buffer = ''
            while bytes_sent < size:
                chunk = self.recv(self.SCP_CHUNK_SIZE)
                file_buffer += chunk
                bytes_sent += len(chunk)
            fd.write(file_buffer)
            LOG.info('Writing file buffer and closing')
            fd.close()
            self.channel.send(self.SCP_ACK)
            self.channel.send_exit_status(0)
            
        # I/O error
        except IOError as e:
            if e.errno == 13:
                LOG.exception('Access to \'%s\' denied: %s' % (self.file, e.strerror))
                self.send_status_and_close(SCP_STATUS[SSH2_FX_PERMISSION_DENIED], SSH2_FX_PERMISSION_DENIED)
            else:
                LOG.exception('Failed to write to file \'%s\': %s' % (self.file, e.strerror))
                self.send_status_and_close(SCP_STATUS[SSH2_FX_FAILURE], SSH2_FX_FAILURE)
                
        # Other exceptions
        except Exception as e:
            LOG.error('SCP error: %s' % str(e))
            self.send_status_and_close('Internal error', SSH2_FX_FAILURE)
        
    """ Wait for Window Adjust """
    def wait_for_adjust(self):
        adj = self.channel.recv(1)
        if adj != self.SCP_WIN_ADJUST:
            LOG.error('Adjust command not received (%r)' % adj)
            raise Exception('Adjust command not received (%r)' % adj)
        
    """ Wait for ACK """
    def wait_for_ack(self):
        ack = self.channel.recv(1)
        if ack != self.SCP_ACK:
            LOG.error('Command not acknowledged (%r)' % ack)
            raise Exception('Command not acknowledged (%r): ' % ack)
        
"""
SCP Interface

Handle SCP data transfers using the opened SSH channel. Used to manage both inbound
and outbound file transfers.
"""
class SCPInterface(SCPServer, threading.Thread):
    
    # Class constructor
    def __init__(self, channel, client):
        super(SCPInterface, self).__init__()
        self.channel = channel
        self.client  = client
        
        # Channel timeout
        self.channel.settimeout(self.SCP_TIMEOUT)
    
    """ Handle SCP Traffic
    
    Handle receiving and transmitting of file contents over the TCP socket between
    client and server. Used to verify file paths, check permissions, etc.
    """
    def run(self, command, client_address):
        try:
            
            # Split the command into a list
            commands   = command.split()
            
            # Remote host
            self.rhost = '%s:%s' % (client_address[0], client_address[1])
            
            # Store the target file and root path
            self.file  = commands[-1]
            self.path  = re.compile(r'(^.*)\\[^\\]*$').sub(r'\g<1>', self.file)
            
            # Directory Copy
            if self.SCP_RECURSIVE in commands:
                LOG.error('Recursive content upload/download not supported')
                self.send_status_and_close(SCP_STATUS[SSH2_FX_OP_UNSUPPORTED], 'Directory upload not supported')
            
            # Inbound Transfer
            if self.SCP_RECEIVE in commands:
                LOG.info('Received inbound file transfer request: [%s] -> [%s]' % (self.rhost, self.file))
                self.receive()
            
            # Outbound Transfer
            elif self.SCP_SEND in commands:
                LOG.info('Received outbound file transfer request: [%s] -> [%s]' % (self.file, self.rhost))
                self.send()
                
            # Invalid Transfer Type
            else:
                self.send_status_and_close(SCP_STATUS[SSH2_FX_OP_UNSUPPORTED], SSH2_FX_OP_UNSUPPORTED)
            
        except SCPException, e:
            LOG.exception('SCP error: %s' % str(e))
            self.send_status_and_close(msg=e, status=e.status)
        except socket.timeout:
            LOG.exception('SCP timeout')
            self.send_status_and_close(msg='%ss timeout' % self.TIMEOUT, status=1)
        except Exception as e:
            LOG.exception('Internal SCP error: %s' % str(e))
            self.send_status_and_close(msg='Internal error', status=1)