import platform

"""
Linux Command Emulator: uname

Class used to emulate the 'uname' command on Windows machines running the CloudScape
SSH server.
"""
class ModUname:
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
        return 'Display detailed system information'
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Run the command
        self.shell['output'].append('%s %s %s %s %s %s' % (platform.system(), platform.node(), platform.release(), platform.version(), platform.machine(), platform.processor()))
        return self.shell