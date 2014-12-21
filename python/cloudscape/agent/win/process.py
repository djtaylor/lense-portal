import os
import sys
import time
import atexit
import string
import random
from importlib import import_module

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.agent.common.config import AgentConfig

# Configuration and logger
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.win.service', CONFIG.log.service)

"""
Process Base Class

A class wrapper used to dynamically inherit the parent class of the process
being spawned.
"""
def _process(base):
    class _Process(base):
        
        # Initialize the subprocess class
        def __init__(self, proc):
            super(_Process, self).__init__()
            LOG.info('[%s]: > Initializing process base class: _Process(%s)' % (proc['name'], proc['class']))
    
            # Register the final exit function
            atexit.register(self._proc_halt_cleanup)
    
            # Process properties
            self.proc = proc
            
        """ Halt Cleanup
        
        Final method that runs before the program exits. Can call any cleanup methods
        here or do final log messages.
        """
        def _proc_halt_cleanup(self):
            LOG.info('[%s]: > Process stopped, running cleanup...' % self.proc['name'])
           
        """ Set Halt Method 
        
        Register a method to use to stop the subprocess if the halt flag is found to
        be true. If no halt flag is found, the subprocess will exit using sys.
        """
        def proc_set_halt(self, method):
            LOG.info('[%s]: > Registering process halt method: %s' % (self.proc['name'], str(method)))
            self.halt = method
            
        """ Check Halt Flag 
        
        Check if the subprocess halt flag is set the true, and run the registered
        halt function if found. If a halt function is not found, do a standard exit.
        If a count number is specified, the method will perform that many 1 second
        loops and exit if the halt flag is found to be true, otherwise it will continue
        the subprocess.
        """
        def proc_check_halt(self, count=None):
            
            # Internal method to check for the halt flag
            def _halt_set():
                return self.proc['halt']
            
            # Internal method to run the halt function
            def _halt_now():
                if hasattr(self, 'halt'):
                    return self.halt()
                else:
                    sys.exit(0)
            
            # Run a loop if a count integer is set
            if count and isinstance(count, int):
                if _halt_set():
                    _halt_now()
                time.sleep(1)
                next = count - 1
                self.proc_check_halt(next)
                
            # Perform a single check if no count integer
            else:
                if _halt_set(): _halt_now()
            return
            
        """ Get Subprocess PID """
        def proc_get_pid(self):
            return self.proc['pid']
    
    # Return the process class
    return _Process
    
"""
Process Parent Class

The following class uses the multiprocessing to emulate forking functionality
found on Linux machines.
"""
class Process:
        
    # Class constructor
    def __init__(self, proc_name, proc_module, proc_class, proc_method):
        
        # Process properties
        self.proc = {
            'name':   proc_name,
            'module': proc_module,
            'class':  proc_class,
            'method': proc_method,
            'halt':   False,
            'pid':    os.getpid()
        }
        
    """ Stop Process """
    def stop(self):
        self.proc['halt'] = True
        
    """ Start Process """
    def start(self):
        LOG.info('[%s]: > Spawning process - PID %s' % (self.proc['name'], self.proc['pid']))
        
        # Load the process module
        module   = import_module(self.proc['module'])     # Import subprocess module
        base_cls = getattr(module, self.proc['class'])    # Get the main subprocess handler class
        sub_cls  = _process(base_cls)                     # Create an inheriting instance of the subprocess wrapper class
        instance = sub_cls(self.proc)                     # Create an instance of the subprocess class tree
        spawn    = getattr(instance, self.proc['method']) # Get the subprocess handler spawn method
        
        # Spawn the process
        spawn()