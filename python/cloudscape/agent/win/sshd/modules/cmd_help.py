"""
Linux Command Emulator: help

Class used to emulate the 'help' command on Windows machines running the CloudScape
SSH server. Used to show available commands an their required and optional parameters.
"""
class ModHelp:
    def __init__(self, chan):
        
        # Connection channel and shell environment
        self.chan    = chan
        self.shell   = None
        self.command = None
    
    """ Set Command Modules """
    def set(self, command):
        self.command = command
    
    """ Help Text """
    def help(self):
        return 'Display this help prompt'
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Run the command
        self.shell['output'].append('')
        for cmd, mod in self.command.iteritems():
            self.shell['output'].append('> {:10s}{:100s}'.format(cmd, mod.help()))
        self.shell['output'].append('')
        return self.shell