import re
import os
import sys
import json
import base64
import tarfile
import subprocess

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common.vars import SYS_TYPE, FORMULA_DIR, FORMULA_LOG, np
from cloudscape.common.utils import FileSec, pyexec
from cloudscape.client.manager import APIConnect
from cloudscape.agent.config import AgentConfig

# Configuration and logger objects
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.formula', CONFIG.agent.log)

"""
Agent Formula Parser

Privileged class file used to parse the result logs from a formula package run. Looks
for either a successful or failed package run, and reports back to the API server.
"""
class AgentFormulaParse(object):

    """ Parse Formula Results """
    def parse(self):
        
        # Formula log files
        if not os.path.isdir(FORMULA_LOG):
            os.mkdir(FORMULA_LOG)
        
        # Find all the log files
        log_files = []
        for log_file in os.listdir(FORMULA_LOG):
            if log_file.endswith('.log'):
                log_files.append(np('%s/%s' % (FORMULA_LOG, log_file)))
        
        # Parse each log file
        if log_files:
            for log_file in log_files:
                LOG.info('Parsing formula results file: %s' % log_file)
                
                # Make sure the file contains log results
                if os.path.getsize(log_file) == 0:
                    continue
                
                # Load the JSON log
                try:
                    log_str  = open(log_file, 'r').read()
                    log_json = json.loads(log_str)
                except:
                    continue
                
                # Construct the results object
                results = {
                    'formula':     log_json['results']['formula'],
                    'sys_uuid':    log_json['results']['sys_uuid'],
                    'end_time':    log_json['results']['end_time'],
                    'exit_code':   str(log_json['results']['exit_code']),
                    'exit_status': log_json['results']['exit_status'],
                    'exit_msg':    log_json['results']['exit_msg'],
                    'log':         base64.b64encode(log_str),
                }
          
                # Return the results object and log file
                LOG.info('Parsed formula log [%s]: %s' % (log_file, json.dumps(results)))
                return log_file, results
            
            # No log files ready for parsing
            return False, False
        
        # No results found
        else:
            return False, False

"""
Agent Formula Executor

Priveleged class file used to execute formula packages with elevated privileges. This
file controls root access to the server for the cloudscape user account. This script
is executed with a single argument, the UUID of the formula package to run.
"""
class AgentFormulaExec(object):
    def __init__(self):

        # File checksum and decryption
        self.fs         = FileSec()
        
        # Package UUID and encryption key
        self.pkg_uuid   = None
        self.dec_key    = None
        
        # Formula registration flag
        self.pkg_reg    = False
        
        # Package script
        self.pkg_script = None
        
        # Decrypted and encrypted package
        self.pkg_enc    = None
        self.pkg_dec    = None
        
        # API connection and client attributes
        self.cs_api     = None
        self.cs_client  = None
        
    # Construct the API client connection
    def _api_connect(self):
        cloudscape_connection = APIConnect(
            user    = CONFIG.agent.uuid, 
            api_key = CONFIG.agent.api_key,
            host    = CONFIG.server.host,
            proto   = CONFIG.server.proto,
            port    = CONFIG.server.port)
        _api, _client = cloudscape_connection.construct()
        
        # Make sure the connection succeeds
        if not _api:
            LOG.error('Failed to connect to API server')
            sys.exit(1)
        else:
            LOG.info('Connected to API server %s://%s:%s' % (CONFIG.server.proto, CONFIG.server.host, CONFIG.server.port))
            return _api, _client
        
    # Register the package
    def _register(self):
        if self.pkg_reg:
            run_rsp = self.cs_api.formula.register({'pkg_uuid': self.pkg_uuid, 'host_uuid': CONFIG.agent.uuid})
            if run_rsp['code'] != 200:
                LOG.error('Failed to register the formula run with API server')
                sys.exit(1)
            LOG.info('Successfully registered the formula run with API server')
            
    # Unpack the formula package
    def _unpack(self):
        pkg_arc = tarfile.open(self.pkg_dec, 'r:gz')
        for item in pkg_arc:
            pkg_arc.extract(item, path=FORMULA_DIR)
        if not os.path.isdir(np('%s/%s' % (FORMULA_DIR, self.pkg_uuid))):
            LOG.error('Could not locate formula package directory after extraction')
            sys.exit(1)
        LOG.info('Unpacked formula archive to: %s\\%s' % (FORMULA_DIR, self.pkg_uuid))
            
        # Set the expected formula script
        self.pkg_script = np('%s/%s/main.py' % (FORMULA_DIR, self.pkg_uuid))
        
        # Make sure the formula script exists
        if not os.path.isfile(self.pkg_script):
            LOG.error('Could not locate formula script at expected location: %s' % self.pkg_script)
            sys.exit(1)
        LOG.info('Discovered formula package script: %s' % self.pkg_script)
            
    # Decrypt the package
    def _decrypt(self):
        self.pkg_dec = np('%s/%s.tar.gz' % (FORMULA_DIR, self.pkg_uuid))
        if not self.fs.decrypt(self.pkg_enc, self.pkg_dec, self.dec_key):
            LOG.error('Failed to decrypt formula package: %s' % self.pkg_enc)
            sys.exit(1)
        
    # Verify the package with the API
    def _verify(self):
        self.pkg_reg = True
        
        # Construct the API connection
        self.cs_api, self.cs_client = self._api_connect()
        
        # Make sure the package exists
        if not os.path.isfile(self.pkg_enc):
            LOG.error('Could not find formula archive at expected location: %s' % self.pkg_enc)
            
        # Generate the hash digest for the file
        pkg_checksum = self.fs.checksum(self.pkg_enc)
        
        # Submit the package verification request
        pkg_rsp = self.cs_api.formula.verify({'pkg_uuid': self.pkg_uuid, 'checksum': pkg_checksum, 'host_uuid': CONFIG.agent.uuid})
        if not 'code' in pkg_rsp:
            LOG.error('Failed to receive a status code response from the API server')
            sys.exit(1)
        if pkg_rsp['code'] != 200:
            LOG.error('HTTP %s: %s' % (pkg_rsp['code'], pkg_rsp['body']))
            sys.exit(1)
        
        # Get the dencryption key
        rsp_obj      = json.loads(pkg_rsp['body'])
        self.dec_key = rsp_obj['key']
        
    # Run the formula package
    def run(self, uuid, dec_key=None):
        self.pkg_uuid = uuid
        self.dec_key  = dec_key
        try:
        
            # Set the expected location of the encrypted package
            self.pkg_enc = np('%s/%s.tar.gz.enc' % (FORMULA_DIR, self.pkg_uuid))
        
            # If no decryption key is specified, verify and get the key
            if not self.dec_key:
                self._verify()
            
            # Decrypt the package
            self._decrypt()
               
            # Unpack the archive
            self._unpack()
                
            # Register the run of the formula
            self._register()
    
            # Set the API arguments
            api_url   = '%s://%s:%s/cloudscape-api' % (CONFIG.server.proto, CONFIG.server.host, CONFIG.server.port)
            api_token = None if not ('token' in self.cs_client) else (self.cs_client['token'])
    
            # Run Script - Windows
            if SYS_TYPE == 'windows':
                code, msg = pyexec(self.pkg_script, api_url=api_url, api_token=api_token)
            
            # Run Script - Linux
            if SYS_TYPE == 'linux':
                proc = subprocess.Popen(['python', self.pkg_script, api_url, api_token], stdout=subprocess.PIPE)
                out, err = proc.communicate()
                
                # Get the exit code and set the message
                code = proc.returncode
                msg  = '' if code == 0 else str(err)
            
            # Get the return code of the script
            if code != 0:
                LOG.error('Failed to run python script, exit code %s: %s' % (code, msg))
                return False
            LOG.info('Successfully ran Python script with exit code %s' % code)
            return True
        
        # Exception when running formula
        except Exception as e:
            LOG.exception('Encountered exception when running formula package [%s]: %s' % (self.pkg_uuid, e.message))
            return False
