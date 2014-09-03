#!/usr/bin/python
import sys
import string

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
        self.msg    = None
        self.width  = 9
        self.stream = sys.stdout
        self.colors = self.has_colors()
        self.color  = { 'red': '31', 'green': '32', 'yellow': '33' }
    
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
    
    def render(self, tag, color=None):
        """
        Format the log message and render depending on the tag type and color.
        Center the tag to the width defined in the class constructor.
        """
        str_aligned = string.center(tag, self.width)
        if self.colors and color:
            msg = '[\x1b[1;%sm%s\x1b[0m]: %s\n' % (color, str_aligned, self.msg)
        else:
            msg = '[%s]: %s\n' % (str_aligned, self.msg)
        sys.stdout.write(msg)
        
    def success(self): 
        """
        Display a success message on the screen.
        """
        self.render('SUCCESS', self.color['green'])
        
    def warn(self): 
        """
        Display a warning message on the screen.
        """
        self.render('WARNING', self.color['yellow'])
        
    def error(self): 
        """
        Display an error message on the screen.
        """
        self.render('ERROR', self.color['red'])

    def info(self): 
        """
        Display an informational message on the screen.
        """
        self.render('INFO')

    def show(self, msg=None):
        """
        Set the message to display with the chosen rendering method.
        
        :param msg: The message to display
        :type msg: str
        :rtype: self
        """
        if not msg:
            return None
        self.msg = msg
        return self