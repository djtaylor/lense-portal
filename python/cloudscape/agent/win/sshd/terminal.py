from __future__ import print_function, unicode_literals
import re
import os
import sys
import ast
import pyte
import copy
import platform
import traceback

# CloudScape Variables
from cloudscape.common.vars import C_HOME

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.agent.common.config import AgentConfig

# SSHD Modules
from cloudscape.agent.win.sshd.modules import cmd_cd
from cloudscape.agent.win.sshd.modules import cmd_ls
from cloudscape.agent.win.sshd.modules import cmd_pwd
from cloudscape.agent.win.sshd.modules import cmd_exit
from cloudscape.agent.win.sshd.modules import cmd_help
from cloudscape.agent.win.sshd.modules import cmd_agent
from cloudscape.agent.win.sshd.modules import cmd_uname
from cloudscape.agent.win.sshd.modules import cmd_service
from cloudscape.agent.win.sshd.modules import cmd_history
from cloudscape.agent.win.sshd.modules import cmd_hostname

# ANSI key values
ANSI_UP    = r'\x1b[A'
ANSI_DOWN  = r'\x1b[B'
ANSI_LEFT  = r'\x1b[D'
ANSI_RIGHT = r'\x1b[C'
ANSI_BS    = r'\x7f'
ANSI_BREAK = r'\x03'
ANSI_TAB   = r'\t'
ANSI_CR    = r'\r'

# Agent configuration and logger
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.win.sshd', CONFIG.log.sshd)

"""
Windows Terminal Emulator

Linux-style terminal interface for SSH sessions. Loads module that emulate the basic
commands available on Linux machines. Because f*ck Windows command prompt, thats why.
"""
class WinTerminal:

    # Class constructor
    def __init__(self):
        
        # Session shell environment
        self.shell   = self._shell_construct()
        
        # Input channel and client connection
        self.channel = None
        self.client  = None
        
        # Command modules
        self.command = {}
        
    """ Construct Shell
    
    Construct the global shell object for this session. Includes the current working
    directory, input and output buffers, command arguments, and the terminal prefix.
    """
    def _shell_construct(self):
        return {
            'home':   C_HOME,       # Home directory
            'cwd':    C_HOME,       # Current working directory
            'input':  '',           # Input buffer
            'output': [],           # Output buffer
            'args':   [],           # Command module arguments
            'ps':     self._set_ps, # Terminal prefix
            'hist':   [],           # Command history
            'hist_i': 0             # Command history index
        }
        
    """ Command Module Mapper
    
    Map of command names to classes found after importing all command modules.
    """
    def _command_mapper(self):
        return {
            'agent':    'ModAgent',
            'cd':       'ModCD',
            'exit':     'ModExit',
            'help':     'ModHelp',
            'hostname': 'ModHostname',
            'ls':       'ModLS',
            'pwd':      'ModPWD',
            'uname':    'ModUname',
            'service':  'ModService',
            'history':  'ModHistory'
        }
        
    """ Load Command Modules
    
    Load all command modules found in the 'modules' directory. Each file emulates a
    common Linux command. Command modules are initialized with the current client channel
    object, and are invoked by calling the 'run' method and passing the existing shell
    object.
    """
    def _load_modules(self):
        try:
            mod_base = 'cloudscape.agent.win.sshd.modules'
            map      = self._command_mapper()
            for cmd_mod, cmd_cls in map.iteritems():
                mod_name   = '%s.cmd_%s' % (mod_base, cmd_mod)
                class_obj  = getattr(sys.modules[mod_name], cmd_cls)
                class_inst = class_obj(self.channel)
                LOG.info('Loading command module: %s' % cmd_mod)
            
                # Add to the utilities object
                self.command[cmd_mod] = class_inst
            
            # Load up the command modules globally
            for mod, obj in self.command.iteritems():
                obj.set(self.command)
        except Exception as e:
            LOG.exception('Failed to load command modules: %s' % repr(e))
        
    """ Set Shell Prefix
    
    Set the shell prefix normally seen on Linux/Unix machines.
    """
    def _set_ps(self):
        if self.shell['cwd'] == self.shell['home']:
            return 'cloudscape@%s:~# ' % platform.node()
        else:
            return 'cloudscape@%s:%s# ' % (platform.node(), self.shell['cwd'])
        
    """ Process User Input
    
    Handle the input string when the user hits the enter key. Strip out the root
    command and arguments. If the command exists in the modules object, pass off
    the current shell. Each command module returns an update shell object.
    """
    def _process_input(self):
        self.shell['hist'].append(self.shell['input'])
        self.shell['hist_i'] = len(self.shell['hist'])
        
        # Get the root command and any arguments
        input = self.shell['input'].split()
        root  = input[0]
        input.pop(0)
        self.shell['args'] = input
        
        # Check if the command is supported
        if root in self.command:
            self.shell           = self.command[root].run(self.shell)
            self.shell['args']   = []
        
        # Clear the screen
        elif root == 'clear':
            self.shell['output'] = 'clear'
        
        # Unsupported command
        else:
            self.shell['output'].append('Command not found, type \'help\' for available commands')
        
    """ Refresh Client Prompt
    
    Send an update command prompt to the client when changing the input buffer.
    Replace the existing line.
    """
    def _refresh_prompt(self):
        self.channel.send('\r%s%s' % (self.shell['ps'](), self.shell['input']))
        
    """ Receive Input
    
    Keep listening to key strokes received over the open SSH socket until the
    enter key is pressed. Update the input buffer depending on the keys pressed,
    and keep refresing the client side channel with the new input buffer.
    """
    def _receive_input(self):
        
        # Trap and ignore these keys
        ignore = [ANSI_RIGHT, ANSI_LEFT, ANSI_UP, ANSI_DOWN, ANSI_TAB]
        
        # Capture user input or command
        try:
            ir = self.channel.recv(1024)
            
            # Get the raw value of the string
            raw = repr(ir).replace("'", "")
            
            # If no input received
            if not raw:
                self._receive_input()
            
            # If submitting the command
            elif raw == ANSI_CR:
                return
        
            # If moving around the history
            elif (raw == ANSI_UP) or (raw == ANSI_DOWN):
                hist_max = len(self.shell['hist'])
                hist_set = False
                if raw == ANSI_UP:
                    if self.shell['hist_i'] == 0:
                        self._receive_input()
                    else:
                        hist_set = True
                        self.shell['hist_i'] = self.shell['hist_i'] - 1
                if raw == ANSI_DOWN:
                    if self.shell['hist_i'] == hist_max:
                        self._receive_input()
                    else:
                        hist_set = True
                        self.shell['hist_i'] = self.shell['hist_i'] + 1
        
                # Get the current input properties
                if hist_set:
                    len_input = len(self.shell['input'])
                    len_hist  = len(self.shell['hist'][self.shell['hist_i']])
                    if len_input >= len_hist:
                        input_new = self.shell['hist'][self.shell['hist_i']].ljust(len_input)
                    else:
                        input_new = self.shell['hist'][self.shell['hist_i']].ljust(len_hist)
            
                    # Return the command in history
                    self.shell['input'] = input_new
                    self._refresh_prompt()
            
                    # Strip out trailing whitespace
                    self.shell['input'] = self.shell['input'].rstrip()
                    self._refresh_prompt()
                    self._receive_input()
        
            # If hitting backspace
            elif raw == ANSI_BS:
                
                # Replace the last character with a space
                self.shell['input'] = self.shell['input'][:-1] + ' '
                self._refresh_prompt()
                
                # Strip out trailing whitespace
                self.shell['input'] = self.shell['input'].rstrip()
                self._refresh_prompt()
                self._receive_input()
        
            # Catch Ctrl+C
            elif raw == ANSI_BREAK:
                self.shell['input'] = ''
                self.channel.send('\r\n')
                self._refresh_prompt()
                self._receive_input()
        
            # Keys to trap and ignore
            elif raw in ignore:
                self._receive_input()
        
            # Standard character
            else:
                self.shell['input'] += raw
                self._refresh_prompt()
                self._receive_input()
        
        # Catch exceptions in reading session input
        except Exception as e:
            LOG.exception('Error in receiving terminal input: %s' % str(e))
            return False
        
    """ Input Prompt
    
    Return the command prompt over the channel, and listen for incoming bytes.
    Pass of handling of incoming bytes to the '_receive_input' method. When the
    return key is pressed, continue this method. Handle the input, look for an
    existing command module, and format and return the output to the client.
    """
    def _prompt_input(self, cleared=False):
    
        # Send the prompt prefix
        if cleared:
            self.channel.send(self.shell['ps']())
        else:
            self.channel.send('\n' + self.shell['ps']())
    
        # Receive user input from the channel
        self._receive_input()
        
        # If the input is empty
        if not self.shell['input'].strip():
            self.channel.send('\r')
            self._prompt_input()
        
        # Process user input
        self._process_input()
        if self.shell['output'] == False:
            return False
        
        # Display any output
        if self.shell['output'] == True:
            self.channel.send('\r')
            
        # Clear the screen
        elif self.shell['output'] == 'clear':
            self.channel.send('\x1b[2J\x1b[H')
            cleared = True
            
        # Render output stream
        else:
            
            # Render output through the client channel
            output = None
            for line in self.shell['output']:
                if not output:
                    output = '\n\r%s' % line
                else:
                    output += '\n\r%s' % line
            output += '\r'
            self.channel.send(output)
            self.screen.reset()
            
        # Reset the input and output buffers
        self.shell['input']  = ''
        self.shell['output'] = []
            
        # Reset the stream and re-prompt for input
        self.stream.reset()
        self._prompt_input(cleared)
       
    """ Show Greeting
    
    Return true right now, but will use in the future to show machine information
    when logging into an SSH session.
    """
    def _show_greeting(self):
        return True
        
    """ Start Terminal
    
    Start the SSH terminal SSH. Receives the SSH channel and client object from the
    server class. Start a new virtual PTY, load command modules, and process user
    input.
    """
    def start(self, channel, client):
        try:
            
            # The SSH channel and client socket connection
            self.channel = channel
            self.client  = client
            LOG.info('Starting new virtual terminal on SSH channel')
            
            # Set this to a blocking session
            self.channel.setblocking(1)
            
            # Show the greeting
            self._show_greeting()
            
            # Create the virtual terminal
            self.stream  = pyte.Stream()
            self.screen  = pyte.Screen(110, 25)
            self.stream.attach(self.screen)
            
            # Load command modules
            self._load_modules()
            
            # Being processing user input
            self._prompt_input()
        except Exception as e:
            traceback.print_exc()
            LOG.exception('Encountered error in Windows terminal: %s' % str(e))
            return False