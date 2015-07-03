import os
import re
import sys
import json
import argparse
import importlib

# Cloudscape Libraries
from cloudscape.common.vars import C_CLIENT, C_MAPPER
from cloudscape.client.manager import APIConnect
from cloudscape.common.utils import format_action
from cloudscape.common.objects import JSONObject

class _CLIModules(object):
    """
    Class object for handling interface modules.
    """
    def __init__(self):
        
        # Internal modules object
        self._modules    = {}
        
        # Help prompt
        self.help_prompt = None
        
    def _construct(self):
        """
        Return a list of supported module arguments.
        """
        
        # Modules help menu
        help_prompt = ''
        
        # Load the client module mapper
        map_json = JSONObject()
        map_json.from_file(C_MAPPER)
        
        # Grab the base module path
        mod_base = map_json.search('base')
        
        # Process each module definition
        for mod in map_json['modules']:
            self._modules[mod['id']] = []
            
            # Load the interface module
            iface_mod = '%s.%s' % (mbase, mod['module'])
            
            # Load the interface request handler
            re_mod   = importlib.import_module(iface_mod)
            re_class = getattr(re_mod, mod['class'])
            
            # Load the public classes for the interface module
            for attr in dir(re_class):
                if not re.match(r'^__.*$', attr):
                    self._modules[mod['id']].append(attr)
            
            # Add the module to the help menu
            help_prompt += format_action(mod['id'], mod['desc'])
        
        # Set the help prompt
        self.help_prompt = help_prompt

class _CLIArgs(object):
    """
    Class object for handling command line arguments.
    """
    def __init__(self):

        # Arguments parser / object
        self.parser  = None
        self._args   = None
        
        # Module help prompt
        self._mhelp  = None
        
        # Construct arguments
        self._construct()
        
    def _return_help(self):
         return ("Cloudscape Client\n\n"
                 "A utility designed to handle interactions with the Cloudscape API client manager.\n"
                 "Supports most of the API endpoints available.\n")
        
    def set_modules_help(self, mhelp):
        """
        Set the modules help prompt.
        """
        self._mhelp = mhelp
        
    def _construct(self):
        """
        Construct the argument parser.
        """
        
        # Create a new argument parsing object and populate the arguments
        self.parser = argparse.ArgumentParser(description=self._return_help(), formatter_class=argparse.RawTextHelpFormatter)
        self.parser.add_argument('module', help=self._mhelp)
        self.parser.add_argument('action', nargs='?', help="The action to perform against the endpoint", action='append')
        self.parser.add_argument('-u', '--api-user', help='The API user to authenticate with if not set as the environment variable "CS_API_USER"', action='append')
        self.parser.add_argument('-g', '--api-group', help='The API user group to authenticate with if not set as the environment variable "CS_API_GROUP"', action='append')
        self.parser.add_argument('-k', '--api-key', help='The API key to authenticate with if not set as the environment variable "CS_API_KEY"', action='append')
        self.parser.add_argument('-d', '--api-data', help='Optional data to pass during the API request', action='append')
        self.parser.add_argument('-l', '--list', help='Show supported actions for a specified module', action='store_true')
      
        # Parse CLI arguments
        sys.argv.pop(0)
        self._args = vars(self.parser.parse_args(sys.argv))
        
    def set(self, k, v):
        """
        Set a new argument or change the value.
        """
        self._args[k] = v
        
    def get(self, k, default=None):
        """
        Retrieve an argument passed via the command line.
        """
        return self._args.get(k, default)

class CLIClient(object):
    """
    Command line interface for making API requests.
    """
    def __init__(self):
    
        # API client and connection parameters
        self.client  = None
        self.connect = None
    
        # Arguments / modules objects
        self.modules = _CLIModules()
        self.args    = _CLIArgs()
        
        # Set the modles help prompt
        self.args.set_modules_help(self.modules.help_prompt)
    
        # API connection attributes
        self._get_api_env()
    
    def _die(self, msg, code=None):
        """
        Print on stderr and die with optional exit code.
        """
        sys.stderr.write(msg)
        sys.exit(code if (code and isinstance(code, int)) else 1)
    
    def _get_api_env(self):
        """
        Look for API connection environment variables.
        """
        
        # Look for environment connection variables
        # If any are found, store them and return
        _api = {}
        for k,v in {
            'api_user':  'CS_API_USER',
            'api_key':   'CS_API_KEY',
            'api_group': 'CS_API_GROUP'
        }.iteritems():
            if v in os.environ:
                self.args.set(k, os.environ[v])
    
    def _connect_api(self):
        """
        Establish an API connection using the client libraries.
        """
        self.client, self.connect = APIConnect(
            user    = self.args['api_user'], 
            group   = self.args['api_group'], 
            api_key = self.args['api_key'], 
            cli     = True
        ).construct()
    
        # If token retrieval/connection failed
        if not self.client:
            response = self.connect['body']
            try:
                response = json.loads(self.connvect['body'])['error']
            except:
                pass
            print 'HTTP %s: %s' % (self.connect['code'], response)
            sys.exit(1)
    
    def _return_modules(self):
        """
        Return a list of supported module arguments.
        """
        
        # Modules help menu
        modules = ''
        
        # Load the client module mapper
        mmap  = '%s/mapper.json' % C_CLIENT
        mjson = json.load(open(mmap))
        mbase = mjson['base']
        
        # Process each module definition
        for mod in mjson['modules']:
            self.modules[mod['id']] = []
            
            # Load the supported module actions
            api_mod = '%s.%s' % (mbase, mod['module'])
            
            # Load the API endpoint handler
            ep_mod   = importlib.import_module(api_mod)
            ep_class = getattr(ep_mod, mod['class'])
            for attr in dir(ep_class):
                if not re.match(r'^__.*$', attr):
                    self.modules[mod['id']].append(attr)
            
            # Add the module to the help menu
            modules += format_action(mod['id'], mod['desc'])
        return modules
    
    def interface(self):
        """
        Handle any command line arguments.
        """
        
        # Handle incoming requests
        try:
        
            # Argument errors
            _req_args = {
                'api_user': 'Missing required argument "api_user"',
                'api_group': 'Missing required argument "api_group"',
                'api_key': 'Missing required argument "api_key"'
            }
            
            _abort = False
            for k,v in self.args.iteritems():
                if (k in _req_args) and not self.args[k]:
                    _abort = True
                    print 'ERROR: %s' % _req_args[k]
            
            if _abort:
                sys.exit(1)
            
            # Establish the API connection
            self._connect_api()
            
            # Process the module argument
            if self.args['module'] in self.modules:
                if self.args['action'][0] in self.modules[self.args['module']]:
                    
                    # Get the client module method
                    mod = getattr(self.client, self.args['module'])
                    act = getattr(mod, self.args['action'][0])
                    
                    # If submitting extra data
                    if self.args['api_data']:
                        response = act(json.loads(self.args['api_data'][0]))
                    else:
                        response = act()
                    
                    # Print the response
                    print 'HTTP %s: %s' % (response['code'], response['body'] if not isinstance(response['body'], (list, dict)) else json.dumps(response['body']))
                    
                # No valid action found
                else:
                    
                    # If listing supported actions
                    if self.args['list']:
                        print '\nSupported actions for module "%s":\n' % self.args['module']
                        for a in self.modules[self.args['module']]:
                            print '> %s' % a
                        print ''
                        sys.exit(0)
                    else:
                        self.ap.print_help()
                        print '\nUnsupported module action "%s"' % self.args['action']
                        print 'Supported actions are: %s\n' % json.dumps(self.modules[self.args['module']])
                        sys.exit(1)
            else:
                self.ap.print_help()
                print '\nUnsupported module argument "%s"\n' % self.args['module']
                sys.exit(1)
        
        # Error in handling arguments
        except Exception as e:
            self._die(str(e))