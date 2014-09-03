from cloudscape.agent.win.base import AgentHandler

"""
Agent Interface

Class used to interface with the Windows Agent libraries from the virtual terminal.
"""
class ModAgent:
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
        return 'CloudScape agent API interface'
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Run the agent command
        msg, code = AgentHandler(args=self.shell['args'], term=True).main()
        self.shell['output'] = msg.split('\n')
        return self.shell
       