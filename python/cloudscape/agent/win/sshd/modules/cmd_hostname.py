import platform

"""
Linux Command Emulator: hostname

Class used to emulate the 'hostname' command on Windows machines running the CloudScape
SSH server.
"""
class ModHostname:
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
        return 'Display the local system\'s hostname'
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Run the command
        self.shell['output'].append(platform.node())
        return self.shell