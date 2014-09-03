import re
import os

"""
Linux Command Emulator: cd

Class used to emulate the 'cd' command on Windows machines running the CloudScape
SSH server. Used to change the 'cwd' global variable.
"""
class ModCD:
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
        return 'Change working directory'
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Handle the directory argument
        if not self.shell['args']:
            self.shell['cwd'] = self.shell['home']
            self.shell['output'] = True
            return self.shell
        
        # Same directory
        elif self.shell['args'][0] == '.':
            self.shell['output'] = True
            return self.shell
        
        # Up one directory
        elif self.shell['args'][0] == '..':
            if re.match(r'^[A-Z]*:\\$', self.shell['cwd']):
                self.shell['output'] = True
                return self.shell
            else:
                parent = re.compile('(^.*\\\)[^\\\]*$').sub(r'\g<1>', self.shell['cwd'])
                if re.match(r'^[A-Z]*:\\$', parent):
                    self.shell['cwd'] = parent
                else:
                    self.shell['cwd'] = parent[:-1]
                self.shell['output'] = True
                return self.shell
        
        # Home alias
        elif self.shell['args'][0] == '~':
            self.shell['cwd'] = self.shell['home']
            self.shell['output'] = True
            return self.shell
        
        # Specific directory
        else:
            target = self.shell['args'][0]
            
            # Absolute path
            if re.match(r'^[A-Z]:\\.*$', target):
                
                # Make sure the directory exists
                if os.path.isdir(target):
                    self.shell['cwd']    = target.replace('\\\\', '\\')
                    self.shell['output'] = True
                    return self.shell
                else:
                    self.shell['output'].append('Target directory does not exist...')
                    return self.shell
                
            # Relative path
            else:
                
                # Make sure the directory exists
                if os.path.isdir('%s\\%s' % (self.shell['cwd'], target)):
                    full_path            = '%s\\%s' % (self.shell['cwd'], target)
                    self.shell['cwd']    = full_path.replace('\\\\', '\\')
                    self.shell['output'] = True
                    return self.shell
                else:
                    self.shell['output'].append('Target directory does not exist...')
                    return self.shell