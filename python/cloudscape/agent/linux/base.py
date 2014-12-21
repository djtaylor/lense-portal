import os
import re
import sys
import time
import json
import signal
import shutil
import resource
import argparse
from requests.exceptions import ConnectionError

# CloudScape Variables
from cloudscape.common.vars import A_RUNNING, A_ERROR, A_STOPPED, \
                                   C_HOME, C_BASE, A_PID, A_CFLAG, A_START, A_STOP, A_RESTART, A_STATUS, \
                                   A_EXECPKG, A_EXECPY, A_EXECWIN, A_SYSINFO, FORMULA_DIR

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common.utils import format_action
from cloudscape.common.feedback import Feedback
from cloudscape.client.manager import APIConnect
from cloudscape.agent.common.config import AgentConfig
from cloudscape.agent.linux.collector import AgentCollector
from cloudscape.agent.formula import AgentFormulaExec, AgentFormulaParse

# Configuration and logger objects
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.linux.api', CONFIG.log.agent)

"""
CloudScape Agent Handler Class
"""
class AgentHandler:
    def __init__(self, args=None):
      
        # API connection and client attributes
        self.api     = None
        self.client  = None
      
        # Set the any passed arguments and the arguments parser
        self.args    = args
        self.ap      = self._set_args()
        
        # Helper classes
        self.fb      = Feedback()
        self.formula = AgentFormulaParse()
        self.collect = AgentCollector()
        
        # Supported actions and action mapper
        self.map     = self._mapper()
      
    """ Set Command Line Arguments """
    def _set_args(self):
        if self.args:
      
            # Create a new argument parsing object and popupate the arguments
            self.ap = argparse.ArgumentParser(description=self._return_help(), formatter_class=argparse.RawTextHelpFormatter)
            self.ap.add_argument('action', help=self._return_actions())
            self.ap.add_argument('-u', '--uuid', help='The UUID of the formula package to execute',
                                 action='append')
          
            # Parse child arguments
            self.args.pop(0)
            args = vars(self.ap.parse_args(self.args))
            self.args = args
            return self.ap
      
    """ Get Agent PID """
    def _get_pid(self):
        if os.path.isfile(A_PID):
            return open(A_PID, 'r').read()
        else:
            return False
      
    """ Set Agent PID """
    def _set_pid(self, pid=None):
        if pid:
            try:
                if not os.path.isdir('%s/run' % C_BASE):
                    os.mkdir('%s/run' % C_BASE)
                open(A_PID, 'w').write(pid)
                return True
            except Exception as e:
                LOG.exception('Failed to set agent process PID file: %s' % e)
                return False
        else:
            LOG.error('Failed to set agent process PID - no PID number found')
            return False
      
    """ Construct API Connetion 
    
    Initialize the connection to the API server for submitting polling data. Make
    this a persistent connection for the agent service.
    """
    def _api_connect(self, trys=6):
        
        # Connect try counter
        connect_trys = trys
        
        # Try to open the API connection
        try:
            cloudscape_connection = APIConnect(
                user    = CONFIG.agent.uuid, 
                api_key = CONFIG.agent.api_key,
                host    = CONFIG.server.host,
                proto   = CONFIG.server.proto,
                port    = CONFIG.server.port)
            _api, _client = cloudscape_connection.construct()
        
            # Make sure the connection succeeds
            if not _api:
                LOG.error('Failed to connect to API server %s://%s:%s, retries left: %d' % (CONFIG.server.proto, CONFIG.server.host, CONFIG.server.port, connect_trys))
                if connect_trys == 0:
                    LOG.error('Could not establish connection to API server, please check your configurating and network settings on both client and server')
                    sys.exit(1)
                time.sleep(5)
                self._api_connect(connect_trys - 1)
            else:
                LOG.info('Connected to API server %s://%s:%s' % (CONFIG.server.proto, CONFIG.server.host, CONFIG.server.port))
            
                # Set the connection objects
                self.api    = _api
                self.client = _client
        
        # Connection refused
        except ConnectionError as e:
            LOG.exception('Connection to API server %s://%s:%s refused, retries left: %d' % (CONFIG.server.proto, CONFIG.server.host, CONFIG.server.port, connect_trys))
            if connect_trys == 0:
                LOG.error('Could not establish connection to API server, please check your configurating and network settings on both client and server')
                sys.exit(1)
            time.sleep(5)
            self._api_connect(connect_trys - 1)
      
    """ Return Help Prompt 
    
    Return available commands when encountering an error in command line arguments.
    """
    def _return_help(self):
        help_prompt = ("CloudScape Agent Manager\n\n"
                       "A utility designed to handler interactions between CloudScape agents on the API\n"
                       "server. Used to handle the agent process for system polling and formula monitoring,\n"
                       "as well as executing formula scripts.")
        return help_prompt
    
    """ Return Actions List 
    
    Return a list of actions available to the agent service.
    """
    def _return_actions(self):
        actions  = format_action(A_START, 'Start the agent poller and formula run monitor')
        actions += format_action(A_STOP, 'Stop the agent poller and formula run monitor')
        actions += format_action(A_RESTART, 'Restart the agent poller and formula run monitor')
        actions += format_action(A_STATUS, 'Return the agent service status')
        actions += format_action(A_EXECPKG, 'Run a formula package on the local system by UUID')
        return actions
      
    """ Collect System Details
    
    Run the first time the polling agent runs. Creates the '.collect' flag file after the
    first run. To re-collect system details, remove this file.
    """
    def _sys_collect(self):
        if not os.path.isfile(A_CFLAG):
            sys_data = self.collect.sys()
            
            # Submit the system details
            LOG.info('Submitting system details: %s' % str(sys_data))
            response = self.api.agent.system(sys_data)
      
            # Log the response
            if response['code'] != 200:
                LOG.error('HTTP %s: %s' % (response['code'], response['body']))
            else:
                LOG.info('HTTP %s: %s' % (response['code'], response['body']))
                
            # Create the collect flag
            open(A_CFLAG, 'w').close()
      
    """ Collect Polling Data 
    
    Collect information about the local system and submit back to the API server.
    """
    def _poll_collect(self):
        
        # Collect the polling data
        poll_data = self.collect.poll()
          
        # Submit the polling request
        LOG.info('Posting system poll statistics to API server: %s' % str(poll_data))
        response = self.api.agent.poll(poll_data)
        
        # Log the response
        if response['code'] != 200:
            LOG.error('HTTP %s: %s' % (response['code'], response['body']))
        else:
            LOG.info('HTTP %s: %s' % (response['code'], response['body']))
         
    """ Parse Formula Results """
    def _formula_parse(self):
        
        # If any results found
        file, results = self.formula.parse()
        if results:
        
            # Post the formula run status
            LOG.info('Posting formula run status to API server: %s' % str(results))
            response = self.api.agent.formula(results)
          
            # Log the response
            if response['code'] != 200:
                LOG.error('HTTP %s: %s' % (response['code'], response['body']))
                shutil.copy(file, '%s.error' % file)
                os.unlink(file)
            else:
                LOG.info('HTTP %s: %s' % (response['code'], response['body']))
                os.unlink(file)
       
    """ Update Agent Status """
    def _set_status(self, status=None):
        if not status:
            return False
        self.api.agent.status({'uuid': CONFIG.agent.uuid, 'status': status})
        return True
         
    """ Check Running Status """
    def _is_running(self):
        pid = self._get_pid()
        if pid:
            try:
                os.kill(int(pid), 0)
                return True
            except Exception as e:
                if os.path.isfile(A_PID):
                    os.remove(A_PID)
                return False
        return False
          
    """ Clear Collector Flag """
    def _cflag_clear(self):
        if os.path.isfile(A_CFLAG):
            os.remove(A_CFLAG)
          
    """ Stop Agent Process """ 
    def _stop(self):
        if self._is_running():
            LOG.info('Stopping CloudScape agent...')
            try:
                self._api_connect()
               
                # Remove the collect flag
                self._cflag_clear()
                
                # Kill the poller process
                os.kill(int(self._get_pid()), 9)
                os.remove(A_PID)
                self._set_status(A_STOPPED)
                return True
            except Exception as e:
                self._set_status(A_ERROR)
                LOG.exception('Failed to stop CloudScape agent process: %s' % e)
                return False
        else:
            LOG.info('CloudScape agent already stopped...')
            if os.path.isfile(A_CFLAG):
                os.remove(A_CFLAG)
            return True
         
    """ Daemon Helper """
    def _daemonize(self):
        
        # Fork a parent process
        try:
            pid = os.fork()
        except OSError, e:
            LOG.exception('Failed to start CloudScape agent: %s' % e)
            sys.exit(1)
        
        # Handle the child process
        if pid == 0:
            try:
                pid = os.fork()
            except OSError, e:
                LOG.exception('Failed to start CloudScape agent: %s' % e)
                sys.exit(1)
            
            # Fork a subprocess to prevent zombies
            if pid == 0:
                os.chdir('/')
                os.umask(0)
                
                # Set the agent process PID
                if not self._set_pid(str(os.getpid())):
                    os._exit(1)
                
                # Connection wrapper    
                def _process():
                
                    # Start the agent process
                    try:
                        LOG.info('Starting CloudScape agent...')
                    
                        # Don't run the system collector as often (every minute)
                        sys_count = 0
                        sys_delay = 1
                    
                        # Set the run interval and start the poller
                        interval = CONFIG.agent.interval
                        while True:
                            time.sleep(int(interval))
                            
                            # Retrieve synchronization data
                            self.collect.synchronize(self.api.agent.sync({'uuid': CONFIG.agent.uuid}))
                            
                            # Scan for formula results
                            self._formula_parse()
                            
                            # Run the system details collector
                            self._sys_collect()
                            
                            # Run the system poller
                            self._poll_collect()
                            
                            # Handle the delay for system collector
                            sys_count += 1
                            if sys_count == sys_delay:
                                sys_count = 0
                                self._cflag_clear()
                            
                            # Check in
                            self._set_status(A_RUNNING)
                            
                    # Connection problem, try to reconnect
                    except ConnectionError as e:
                        LOG.exception('Lost connection with CloudScape API server, attempting reconnect...')
                            
                        # Try to reconnect
                        self._api_connect()
                        _process()
                            
                    # Process terminated early
                    except Exception as e:
                        self._set_status(A_ERROR)
                        LOG.exception('CloudScape agent process terminated with error: %s' % e)
                        os._exit(1)
            
                # Start the polling process
                _process()
                        
            # Update the agent status and exit
            else:
                self._set_status(A_RUNNING)
                os._exit(0)
                
        # Exit the parent
        else:
            os._exit(0)
           
        # Close any file descriptors opened by the parent
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = 1024
        for fd in range(0, maxfd):
            try:
                os.close(fd)
            except OSError:
                pass
           
        # Direct everything to /dev/null
        os.open(os.devnull, os.O_RDWR)
           
        # Duplicate standard input to standard output and error 
        os.dup2(0, 1)
        os.dup2(0, 2)
        return True
            
    """ Start Agent Process """
    def _start(self):
        if not self._is_running():
            self._api_connect()
            
            # Daemonize the process
            if not self._daemonize():
                return False
            return True
        else:
            LOG.info('CloudScape agent is currently running [%s]...' % self._get_pid)
            return True
          
    """ Restart Agent Process """
    def _restart(self):
        
        # Stop the process if running
        if self._is_running():     
            if not self._stop():
                self.fb.show('Failed to stop CloudScape agent...').error()
                os._exit(1)
            self.fb.show('Stopped CloudScape agent...').success()
        
        # Refork the process
        pid = os.fork()
        if pid == 0:
            self._start()
        else:
            time.sleep(1)
            if self._is_running():
                self.fb.show('Started CloudScape agent [PID %s]...' % self._get_pid()).success()
                os._exit(0)
            else:
                self.fb.show('Failed to start CloudScape agent...').error()
                os._exit(1)
        
    """ Agent Status """
    def _status(self):
        if not self._is_running():
            self.fb.show('CloudScape agent is currently stopped...').info()
        else:
            self.fb.show('CloudScape agent is currently running [%s]...' % self._get_pid()).info()
        
    """ System Information """
    def _sysinfo(self):
        print json.dumps(self.collect.sys())
        
    """ Execute Formula Package """
    def _exec_pkg(self):
        if not self.args['uuid']:
            self.ap.print_help()
            self.ap.exit(status=1, message='\nYou must supply a UUID to run a formula package\n')
            
        # Set the package UUID
        pkg_uuid = self.args['uuid'][0]
            
        # If the formula package doesn't exist
        if not os.path.isfile('%s/%s.tar.gz.enc' % (FORMULA_DIR, pkg_uuid)):
            self.ap.print_help()
            self.ap.exit(status=1, message='\nThe UUID you specified does not exist in the formula packages directory\n')
            
        # Load the formula executor
        if not AgentFormulaExec().run(pkg_uuid):
            sys.stderr.write('Failed to run formula package [%s]' % pkg_uuid)
            sys.exit(1)
        sys.stdout.write('Successfully ran formula package [%s]' % pkg_uuid)
        sys.exit(0)
            
    """ Action Mapper """
    def _mapper(self):
        return {
            A_START:   self._start,
            A_STOP:    self._stop,
            A_RESTART: self._restart,
            A_STATUS:  self._status,
            A_EXECPKG: self._exec_pkg,
            A_SYSINFO: self._sysinfo
        }
            
    """ Command Line Interpreter """
    def main(self):
        if not self.args['action'] in self.map:
            self.ap.print_help()
            self.ap.exit()
            
        # Run the action method
        LOG.info('Handling command line argument: %s' % self.args['action'])
        self.map[self.args['action']]()