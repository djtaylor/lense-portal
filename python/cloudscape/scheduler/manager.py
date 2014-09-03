import os
import re
import sys
import importlib
from threading import Thread

# CLoudScape Libraries
import cloudscape.common.config as config
import cloudscape.common.logger as logger
from cloudscape.common.feedback import Feedback
from cloudscape.common.vars import L_BASE

# Module class name
MOD_CLASS = 'ScheduleModule'

class ScheduleManager(object):
    """
    Main class for running scheduled CloudScape tasks.
    """
    def __init__(self, args):
        """
        Initialize the schedule manager and store any command line arguments.
        """
        
        # Configuration / logger
        self.conf     = config.parse()
        self.log      = logger.create(__name__, self.conf.scheduler.log)
        
        # Modules / threads
        self.modules  = {}
        self.threads  = []
        
        # Load all scheduler modules
        self._load_modules()
       
    def _module_worker(self, name, handler):
        """
        Worker method for each module thread.
        """
        try:
            
            # Launch the scheduler module handler
            self.log.info('Starting <%s> scheduler module thread: %s' % (name, handler))
            handler().launch()
            
        # Critical error in scheduler module
        except Exception as e:
            self.log.exception('Critical error when running scheduler module <%s>: %s' % name, str(e))
        
    def _load_modules(self):
        """
        Load all scheduler modules.
        """
        
        # Module directory / base path
        mod_path = '%s/python/cloudscape/scheduler/module' % L_BASE
        mod_base = 'cloudscape.scheduler.module'
        
        # Scan every module file
        for r,d,f in os.walk(mod_path):
            for m in f:
                try:
                
                    # Ignore special files
                    if re.match(r'^__.*$', m) or re.match(r'^.*\.pyc$', m):
                        continue
                    
                    # Get the file module name
                    mod_file = re.compile(r'(^[^\.]*)\..*$').sub(r'\g<1>', m)
                    
                    # Define the module name
                    mod_name = '%s.%s' % (mod_base, mod_file)
                    
                    # Create a new module instance
                    mod_obj  = importlib.import_module(mod_name)
                    cls_obj  = getattr(mod_obj, MOD_CLASS)
                    
                    # Add to the modules object
                    self.modules[mod_file] = cls_obj
                    
                    # Log the constructed module
                    self.log.info('Loading scheduler module: name=%s, class=%s, object=%s' % (mod_name, MOD_CLASS, repr(cls_obj)))
                    
                # Failed to import module
                except Exception as e:
                    self.log.exception('Failed to load scheduler module <%s.%s>: %s' % (mod_file, MOD_CLASS, str(e)))
                    sys.exit(1)
        
    def run(self):
        """
        Worker method for running the CloudScape schedule manager.
        """
        
        # Launch the scheduler modules
        for mod_name, mod_obj in self.modules.iteritems():
            
            # Create the thread
            thread = Thread(target=self._module_worker, args=[mod_name, mod_obj])
            
            # Store the thread then start
            self.threads.append(thread)
            thread.start()
        