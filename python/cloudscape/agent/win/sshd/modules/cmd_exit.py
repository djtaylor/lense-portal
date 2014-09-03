"""
Linux Command Emulator: exit

Class used to emulate the 'exit' command on Windows machines running the CloudScape
SSH server. Terminates the session.
"""
class ModExit:
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
        return 'Close the SSH session'
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Run the command
        self.chan.send('\r\n')
        self.shell['output'] = False
        return self.shell