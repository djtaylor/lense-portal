import re
import os
import stat
import time

"""
Linux Command Emulator: ls

Class used to emulate the 'ls' command on Windows machines running the CloudScape
SSH server. Show contents of directories.
"""
class ModLS:
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
        return 'List contents of the file system'
    
    """ Convert Size (Human Readable) """
    def _convert_size(self, size):
        
        # KB
        if size > 1024 and size <= 1048576:
            size_str  = float(size) / 1024
            size_unit = 'K'
        
        # MB
        elif size > 1048576 and size <= 1073741824:
            size_str  = float(size) / 1048576
            size_unit = 'M'
        
        # GB
        elif size > 1073741824 and size <= 1099511627776:
            size_str  = float(size) / 1073741824
            size_unit = 'G'
        
        # B
        else:
            size_str  = size
            size_unit = ''
        return '%s%s' % ('%.1f' % size_str, size_unit)
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # If no arguments provided, flat list of working directory
        if not self.shell['args']:
            contents = os.listdir(self.shell['cwd'])
            self.shell['output'].append('')
            self.shell['output'].append('{:6s}{:26s}{:>12s}  {:<20s}'.format('Mode', 'Modified', 'Size', 'Name'))
            self.shell['output'].append('{:6s}{:26s}{:>12s}  {:<20s}'.format('----', '--------', '----', '----'))
            for t in contents:
                permissions = oct(stat.S_IMODE(os.stat('%s\\%s' % (self.shell['cwd'], t)).st_mode))
                modified    = time.ctime(os.stat('%s\\%s' % (self.shell['cwd'], t)).st_mtime)
                size        = self._convert_size(os.stat('%s\\%s' % (self.shell['cwd'], t)).st_size)
                name        = t
                self.shell['output'].append('{:6s}{:26s}{:>12s}  {:<20s}'.format(permissions, modified, size, name))
            self.shell['output'].append('')
            return self.shell
            
        # Process arguments
        else:
            self.shell['output'] = True
            return self.shell