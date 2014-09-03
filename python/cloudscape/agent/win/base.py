import os
import re
import sys
import time
import json
import argparse
import subprocess
from requests.exceptions import ConnectionError

# CloudScape Variables
from cloudscape.common.vars import A_RUNNING, A_ERROR, A_STOPPED, \
                                   A_EXECPKG, A_EXECPY, A_EXECWIN, A_SYSINFO, \
                                   C_BASE, C_HOME, A_CFLAG

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common.utils import pyexec, format_action
from cloudscape.client.manager import APIConnect
from cloudscape.agent.config import AgentConfig
from cloudscape.agent.win.collector.interface import CollectorInterface
from cloudscape.agent.formula import AgentFormulaParse, AgentFormulaExec

# Configuration and logger objects
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.win.api', CONFIG.log.agent)

"""
CloudScape Windows Agent Handler Class
"""
class AgentHandler(object):
    def __init__(self, args=None, term=False):
        self.term    = term
        
        # Set the any passed arguments and the arguments parser
        self.args    = args
        self.ap      = self._set_args()
        
        # API connection objects
        self.api     = None
        self.client  = None
        
        # Initialize API connection
        self._api_connect()
        
        # Supported actions and action mapper
        self.map     = self._mapper()
     
    """ Check Activation Status """
    def _active(self):
        if not CONFIG.agent.uuid or not CONFIG.agent.api_key:
            return False
        return True
        
    """ Set Command Line Arguments """
    def _set_args(self):
        usage = 'agent [-h] [-u UUID] [-d KEY] [-c COMMAND] [-s SCRIPT] action'
        LOG.info('Parsing agent handler arguments: %s' % str(self.args))
      
        # Create a new argument parsing object and popupate the arguments
        ap = argparse.ArgumentParser(description=self._return_help(), usage=usage, formatter_class=argparse.RawTextHelpFormatter)
        ap.add_argument('action', help=self._return_actions())
        ap.add_argument('-u', '--uuid', help='[exec-pkg]: The UUID of the formula package to execute', action='append')
        ap.add_argument('-d', '--decrypt', help='[exec-pkg]: Supply a decryption key to bypass normal package execution steps', action='append')
        ap.add_argument('-c', '--cmd', help='[exec-win]: The Windows command string to run', action='append')
        ap.add_argument('-s', '--script', help='[exec-py]: A Python script to run using the embedded libraries', action='append')
      
        # Parse child arguments
        if self.args:
            if not self.term:
                self.args.pop(0)
            try:
                args = vars(ap.parse_args(self.args))
            except SystemExit:
                return self._exit(msg='Missing required arguments', code=1)
            self.args = args
        return ap
        
    """ Return Help Prompt 
    
    Return available commands when encountering an error in command line arguments.
    """
    def _return_help(self):
        help_prompt = ("CloudScape Agent Manager\n\n\r"
                       "A utility designed to handler interactions between CloudScape agents on the API\n\r"
                       "server. Used to handle the agent process for system polling and formula monitoring,\n\r"
                       "as well as executing formula scripts.")
        return help_prompt
    
    """ Return Actions List 
    
    Return a list of actions available to the agent service.
    """
    def _return_actions(self):
        actions  = format_action(A_EXECPKG, 'Run a formula package on the local system by UUID', b=True)
        actions += format_action(A_EXECWIN, 'Run a native Windows command', b=True)
        actions += format_action(A_EXECPY, 'Run a Python script using the embedded libraries', b=True)
        actions += format_action(A_SYSINFO, 'Return a JSON object of system information', b=True)
        return actions
        
    """ Construct API Connetion 
    
    Initialize the connection to the API server for submitting polling data. Make
    this a persistent connection for the agent service.
    """
    def _api_connect(self, trys=6):
        if not self._active():
            LOG.info('Skipping API connection, server not yet activated')
        else:
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
                        return self._exit(msg='Failed to connect to the API server', code=1)
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
                    return self._exit(msg='Failed to connect to the API server', code=1)
                time.sleep(5)
                self._api_connect(connect_trys - 1)
        
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
          
            # Remove the log file
            os.remove(file)
          
            # Log the response
            if response['code'] != 200:
                LOG.error('HTTP %s: %s' % (response['code'], response['body']))
            else:
                LOG.info('HTTP %s: %s' % (response['code'], response['body']))
       
    """ Update Agent Status """
    def _set_status(self, status=None):
        if not status:
            return False
        self.api.agent.status({'uuid': CONFIG.agent.uuid, 'status': status})
        return True
        
    """ Exit Handler """
    def _exit(self, msg=None, code=0):
        if not self.term:
            print msg
            sys.exit(code) 
        else:
            return msg, code
       
    """ Extract System Information """
    def _sysinfo(self):
        
        # Helper classes
        self.collect = CollectorInterface()
        
        # Return system information
        return self._exit(json.dumps(self.collect.sys()), 0)
       
    """ Run Python Script """
    def _exec_py(self):
       if not 'script' in self.args or not self.args['script']:
           return self._exit('Must specify the path to a Python script using [-s "C:\example.py"]', 1)
       
       # Try to run the Python script
       code, msg = pyexec(self.args['script'][0])
       if code != 0:
           return self._exit('Failed to run Python script: %s' % str(msg), code)
       return self._exit('Successfully ran Python script', 0)
       
    """ Run Windows Command """
    def _exec_win(self):
       if not 'cmd' in self.args or not self.args['cmd']:
           return self._exit('Must specify a command string using [-c "some.exe command"]', 1)
       cmd = self.args['cmd'][0].split()
       
       # Run the command (I should probably parse the string for security reasons first)
       proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       out, err = proc.communicate()
       
       # Check the exit code
       exit_code = proc.returncode
       if exit_code != 0:
           return self._exit('Failed to run command: [%s] - exit code %s' % (' '.join(cmd), exit_code))
       return self._exit('Successfully ran command: [%s] - exit code %s' % (' '.join(cmd), exit_code))
       
    """ Execute Formula Package """
    def _exec_pkg(self):
        if not 'uuid' in self.args or not self.args['uuid']:
            return self._exit('You must supply a UUID to run a formula package using --uuid UUID', 1)
        pkg_uuid = self.args['uuid'][0]
            
        # If the formula package doesn't exist
        if not os.path.isfile('%s\\%s.tar.gz.enc' % (FORMULA_DIR, pkg_uuid)):
            return self._exit('The UUID you specified [%s] does not exist in the formula packages directory' % pkg_uuid, 1)
       
        # Optional decryption key
        dec_key = None if not 'decrypt' in self.args else self.args['decrypt'][0]
        
        # Execute the package
        if not AgentFormulaExec().run(pkg_uuid, dec_key):
            return self._exit('Failed to run formula package [%s]' % pkg_uuid, 1)
        return self._exit('Successfully ran formula package [%s]' % pkg_uuid, 0)
       
    """ Start Agent Process """
    def start(self):
        LOG.info('Starting CloudScape agent...')
        
        # Helper classes
        self.collect = CollectorInterface()
        self.formula = AgentFormulaParse()
        
        # Set the halt method to be called when the halt flag is set to true
        self.proc_set_halt(self.stop)
        
        # Only start if the agent is active
        if self._active():
    
            # Connection wrapper    
            def _process():
                try:
                
                    # Start the poller
                    while True:
                        self._set_status(A_RUNNING)
                        
                        # Look for a halt flag
                        self.proc_check_halt(CONFIG.agent.interval)
                        
                        # Scan for formula results
                        self._formula_parse()
                        
                        # Run the system details collector
                        self._sys_collect()
                        
                        # Run the system poller
                        self._poll_collect()
                        
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
            
        # Agent hasn't been activated yet
        else:
            LOG.info('CloudScape agent not starting, not activated by API server yet...')
    
    """ Stop Agent Process """
    def stop(self):
        LOG.info('Shutting down CloudScape agent...')
        self._set_status(A_STOPPED)
        sys.exit(0)
       
    """ Action Mapper """
    def _mapper(self):
        return {
            A_EXECPKG: self._exec_pkg,
            A_EXECWIN: self._exec_win,
            A_EXECPY:  self._exec_py,
            A_SYSINFO: self._sysinfo,
        }
            
    """ Command Line Interpreter """
    def main(self):
        try:
            if not self.args or not 'action' in self.map:
                return self._exit('Missing required arguments, try agent --help', 1)
            if not self.args['action'] in self.actions:
                return self._exit('Using unsupported action argument [%s]' % self.args['action'], 1)
                
            # Run the action method
            LOG.info('Handling command line argument: %s' % self.args['action'])
            return self.map[self.args['action']]()
        
        # Exception in agent process - FAIL
        except Exception as e:
            LOG.exception('Encountered agent exception: %s' % str(e))
            return self._exit('Internal error', 1)
