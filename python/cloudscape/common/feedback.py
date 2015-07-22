#!/usr/bin/python
import sys
import copy
import string
from getpass import getpass

class Feedback:
    """
    Class used to print feedback at the command line when running interactive commands.
    Will display in colors if the terminal supports it.
    
    Rendering feedback in the terminal::
    
        # Import the feedback class
        from cloudscape.common.feedback import Feedback
        
        # Create a feedback object
        fb = Feedback()
        
        # Render different messages
        fb.show('Command was OK').success()
        fb.show('You might want to know this').info()
        fb.show('Something bad happened').error()
    """
    def __init__(self):
        """
        Initialize the feedback object. Checks to see if the terminal supports colors,
        otherwise sets to the default terminal text color.
        """
        self.msg      = None
        self.width    = 9
        self.stream   = sys.stdout
        self.colors   = self.has_colors()
        self.color    = { 'red': '31', 'green': '32', 'yellow': '33' }
        self.response = None
    
    def get_response(self):
        """
        Return then clear the response variable.
        """
        _response = copy.copy(self.response)
        self.response = None
        return _response
    
    def has_colors(self):
        """
        Check if the terminal supports colors
        
        :rtype: boolean
        """
        if not hasattr(self.stream, 'isatty'):
            return False
        if not self.stream.isatty():
            return False
        try:
            import curses
            curses.setupterm()
            return curses.tigetnum('colors') > 2
        except:
            return False
    
    def render(self, tag, **kwargs):
        """
        Format the log message and render depending on the tag type and color.
        Center the tag to the width defined in the class constructor.
        """
        
        # Align and format the output string
        str_aligned = string.center(tag, self.width)
        str_format  = (('\r' if kwargs.get('refresh', False) else ''), ('\n' if kwargs.get('newline', True) else ''))
        
        # If outputting with colors
        if self.colors and kwargs.get('color'):
            msg = '%s[\x1b[1;%sm%s\x1b[0m]: %s%s' % (str_format[0], kwargs.get('color'), str_aligned, self.msg, str_format[1])
        
        # No colors
        else:
            msg = '%s[%s]: %s%s' % (str_format[0], str_aligned, self.msg, str_format[1])
        
        # If capturing input
        if kwargs.get('input_get'):
            msg_input = '[{}]: {}'.format(string.center('INPUT', self.width), self.msg)
            
            # If using a secure prompt
            if kwargs.get('input_secure'):
                
                # Confirm the input
                if kwargs.get('input_confirm'):
                    msg_confirm = '[{}]: Please re-enter the value: '.format(string.center('CONFIRM', self.width))
                    
                    # Input / confirmation prompts
                    prompt = lambda: (getpass(msg_input), getpass(msg_confirm))
        
                    # Get input and confirm
                    def _get_and_confirm_input():
                        val_one, val_two = prompt()
                        if not val_one == val_two:
                            sys.stdout.write('[\x1b[1;{}m{}\x1b[0m]: Values do not match, please try again...\n'.format(self.color['red'], string.center('ERROR', self.width)))
                            return _get_and_confirm_input()
                        return val_one
                    self.response = _get_and_confirm_input()
                    
                # No confirmation needed
                else:
                    self.response = getpass(prompt=msg_input)
                
            # Plain text prompt
            else:
                
                # If parsing a yes/no answer
                if kwargs.get('input_yn', False):
                    def _get_yn_response():
                        _response = raw_input(msg_input)
                        _response = _response.lower()
                        if _response != 'y' and _response != 'n': 
                            sys.stdout.write('[\x1b[1;{}m{}\x1b[0m]: Response must be "y" or "n"...\n'.format(self.color['red'], string.center('ERROR', self.width)))
                            return _get_yn_response()
                        return True if _response == 'y' else False
                    self.response = _get_yn_response()
                else:
                    self.response = raw_input(msg_input)
            
        # Write straight to stdout
        else:
            sys.stdout.write(msg)
        
    def success(self): 
        """
        Display a success message on the screen.
        """
        self.render('SUCCESS', color=self.color['green'])
        
    def warn(self): 
        """
        Display a warning message on the screen.
        """
        self.render('WARNING', color=self.color['yellow'])
        
    def error(self): 
        """
        Display an error message on the screen.
        """
        self.render('ERROR', color=self.color['red'])

    def block(self, label='INFO'):
        """
        Display a block of indented text.
        """
        self.render(label, newline=False)

    def progress(self, percent=0):
        """
        Display a progress bar.
        """
        bar_total = 60
        bar_count = int(float(bar_total) * (float(percent)/float(100)))
        
        # Set the progress bar
        self.msg  = '[%s%s] %d%%' % (('#' * bar_count), (' ' * (bar_total - bar_count)), percent)
        
        # Progress complete
        if percent == 100:
            self.msg += '\n'
        self.render('PROGRESS', refresh=True)

    def input(self, secure=False, confirm=False, yes_no=False):
        """
        Display an input prompt on the screen.
        """
        self.render('INPUT', input_get=True, input_secure=secure, input_confirm=confirm, input_yn=yes_no)

    def info(self): 
        """
        Display an informational message on the screen.
        """
        self.render('INFO')

    def show(self, msg=None, **kwargs):
        """
        Set the message to display with the chosen rendering method.
        
        :param msg: The message to display
        :type msg: str
        :rtype: self
        """
        if isinstance(msg, str):
            self.msg = msg
        elif isinstance(msg, list):
            indent   = self.width + 4
            count    = 0
            self.msg = ''
            for line in msg:
                indent_str = '' if count == 0 else ' ' * indent
                self.msg += '{}{}\n'.format(indent_str, line)
                count += 1
        else:
            return self
        return self