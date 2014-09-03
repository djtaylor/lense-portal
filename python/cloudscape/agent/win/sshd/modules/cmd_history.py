"""
Linux Command Emulator: history

Class used to emulate the 'history' command on Windows machines running the CloudScape
SSH server. Used to show commands in the history buffer.
"""
class ModHistory:
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
        return 'Show commands in the history buffer'
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Run the command
        self.shell['output'].append('')
        counter = 1
        for command in self.shell['hist']:
            self.shell['output'].append(' {:^3d} {:100s}'.format(counter, command))
            counter += 1
        self.shell['output'].append('')
        return self.shell