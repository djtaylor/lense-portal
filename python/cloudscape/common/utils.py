import re
import os
import sys
import json
import uuid
import psutil
import struct
import string
import random
import hashlib
import operator
import importlib
import subprocess
from Crypto.Cipher import AES

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.agent.config import AgentConfig
from cloudscape.common.vars import SYS_TYPE, A_CONF, S_CONF, PY_WRAPPER, PY_BASE, np

def rstring(length=12):
    """
    Helper method used to generate a random string.
    """
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(length)])

def pyexec(script, **kwargs):
    """
    Run a Python script using the embedded Python library in the Windows CloudScape
    agent. Executes a batch script that acts as the Python wrapper, setting environment
    variables such as PATH and PYTHONPATH during runtime.
    
    Excepts and API URL and token as optional arguments if running a formula package
    that needs to connect to the API server.
    
    Running a script using the embedded Python library::
    
        # Import the utility
        from cloudscape.common.utils import pyexec
        
        # Run the sript
        code, err = pyexec('C:\path\to\script.py')
        
        # Check for an error code
        if code != 0:
            raise Exception(str(e))
    
    :param script: The path to the script to execute
    :type script: str
    """
    
    # Make sure the script exists
    if not os.path.isfile(script):
        return 1, 'File not found: %s' % script
        
    # Set API parameters
    api_url   = None if not ('api_url' in kwargs) else (kwargs['api_url'])
    api_token = None if not ('api_token' in kwargs) else (kwargs['api_token'])
        
    # Run the script
    proc = subprocess.Popen([PY_WRAPPER, PY_BASE, script, api_url, api_token], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    
    # Get the exit code
    exit_code = proc.returncode
    if not exit_code == 0:
        return exit_code, str(err)
    return exit_code, None

def autoquote(v):
    """
    Autoquote a return value. If the value is a string, quote and return. If the
    object is a type of number, do not quote. If the object is boolean or an
    object, return a representation.
    """
    
    # Int / Float / Long / Complex
    if (isinstance(v, int)) or (isinstance(v, float)) or (isinstance(v, long)) or (isinstance(v, complex)):
        return v
    
    # True / False / None / List / Dictionary
    elif (v == None) or (v == False) or (v == True) or (isinstance(v, list)) or (isinstance(v, dict)):
        return repr(v)
    
    # String / Unicode / etc.
    else:
        return '\'%s\'' % v

def mod_has_class(mod, cls, no_launch=False):
    """
    Helper method used to check if a module file contains a class definition.
    
    :param mod: The path to the module to inspect
    :type mod: str
    :param cls: The class definition name
    :type cls: str
    """

    # Try to import the module
    try:
        mod_inst = importlib.import_module(mod)
        
        # Make sure the module has the class definition
        if not hasattr(mod_inst, cls):
            return invalid('Class definition <%s> not found in module <%s>' % (cls, mod))
        
        # Create an instance of the class
        cls_inst = getattr(mod_inst, cls)
        if not no_launch:
            if not hasattr(cls_inst, 'launch') or not callable(cls_inst.launch):
                return invalid('Class <%s.%s> requires a callable <launch> method definition' % (mod, cls))
        return valid()
    except Exception:
        return invalid('Failed to import module <%s>: %s' % (mod, str(e)))

def obj_extract(obj, id=None, filter=None, auto_quote=True):
    """
    Helper method used to extract details from a JSON object structure
    depending on a root ID (optional) and a filter.
    
    :param obj: The JSON object to extract from
    :type obj: list|dict
    :param id: The optional root ID if using a multi key object
    :type id: str
    :param filter: The object filter as parsed by this method
    :type filter:
    :rtype: str
    """
    if not id and not filter:
        return obj
    
    # Get the base object
    base_obj = obj if not id else obj[id]
    
    # If no filter specified
    if not filter:
        return obj if not (id in obj) else obj[id]
    
    # Break up the filter
    fv = filter.split('.')
    
    # Extract the data
    def _inner(_obj, _fv):
        if isinstance(_obj, list):
            for o in _obj:
                if re.match(r'^\[.*\]$', _fv[0]):
                    lv = re.compile(r'^\[(.*)\]$').sub(r'\g<1>', _fv[0])
                    for k,v in o.iteritems():
                        if lv == v:
                            _fv.pop(0)
                            if _fv[0] in o:
                                return _inner(o, _fv)
                if _fv[0] in o:
                    _fv.pop(0)
                    return _inner(o, _fv)
        if isinstance(_obj, dict):
            for k,v in _obj.iteritems():
                if len(_fv) == 1:
                    if k == _fv[0]:
                        return v if not auto_quote else autoquote(v)
                else:
                    if k == _fv[0]:
                        _fv.pop(0)
                        return _inner(v, _fv)
    return _inner(base_obj, fv)

def find_restop(type='memory', c=10):
    """
    Helper method to find the top processes consuming system resources. Can find
    either CPU or memory usage with a variable number of processes. Defaults to 
    finding the top 10 processes using memory.
    
    Processes are sorted by most intensive.
    
    Finding resource consuming processes::
    
        # Import the utility
        from cloudscape.common.utis import find_restop
        
        # Find memory intensive processes
        mem = find_restop(type='memory', c=20)
        
        # Find CPU intensive processes
        cpu = find_restop(type='cpu', c=10)
    
    :param type: Find 'memory' or 'cpu' usage
    :type type: str
    :param c: The number of processes to find
    :type c: int
    :rtype: list
    """
    res_sort = {}
    res_map  = {}
    for proc in psutil.process_iter():
        try:
            pd = psutil.Process(proc.pid)
            if callable(pd.name):
                pn = pd.name()
            else:
                pn = pd.name

            # Filter by memory usage
            if type == 'memory':
                pm = pd.get_memory_info()
                res_sort[proc.pid] = pm.rss
                res_map[proc.pid] = {'name': pn, 'pid': proc.pid, 'rss': pm.rss, 'vms': pm.vms}

            # Filter by CPU usage
            if type == 'cpu':
                pm = pd.get_cpu_percent(interval=0.1)
                res_sort[proc.pid] = pm
                res_map[proc.pid] = {'name': pn, 'pid': proc.pid, 'percent': pm}
        except:
            pass
    _sort = sorted(res_sort.iteritems(), key=operator.itemgetter(1))
    top   = _sort[-c:]
    top.reverse()
    top_r = []
    for i in top:
        pid = i[0]
        if type == 'memory':
            top_r.append({'pid': pid, 'name': res_map[pid]['name'], 'rss': res_map[pid]['rss'], 'vms': res_map[pid]['vms']})
        if type == 'cpu':
            top_r.append({'pid': pid, 'name': res_map[pid]['name'], 'percent': res_map[pid]['percent']})
    return top_r

class CmdEmbedded:
    """
    Helper class used by the Windows agent to intercept embedded commands
    that should be passed directly to the application instead of being handled
    by the Windows service classes.
    """
    def __init__(self, cli_args):
        """
        Initialize the embedded command filter.
        
        :param cli_args: Any command line arguments
        :type cli_args: list
        """
        self.cli_args  = cli_args

        # Embedded command map
        self._cmd      = None
        self._cmd_map  = {}

    def set_embedded(self, cmd_map):
        """
        Set a map of command arguments and handler methods.
        
        :param cmd_map: A dictionary of command arguments and helper methods
        :type cmd_map: dict
        """
        for cmd, handler in cmd_map.iteritems():
            self._cmd_map[cmd] = handler
            
    def is_embedded(self):
        """
        Check if running an embedded command by scanning the command line arguments.
        Set the embedded command handler if found. Return true if found, false otherwise.
        
        :rtype: boolean
        """
        for cmd, handler in self._cmd_map.iteritems():
            if cmd in self.cli_args:
                self._cmd = cmd
                return True
        return False
    
    def get_embedded(self):
        """
        If running an embedded command, return the command handler method.
        
        :rtype: method
        """
        return self._cmd_map[self._cmd]

def valid(msg=None, data=None):
    """
    Return valid request object. Used internally by the API to pass data between methods.
    Contains a boolean 'valid' flag as well as the data to return to the calling method.
    
    Example usage::
    
        # Import the utilities
        from cloudscape.common.utils import valid, invalid
    
        # Some external class
        from awesome.module import Constructor
    
        # Some internal class
        class APIClass:
        
            # Some internal method
            def _im_internal(self):
                
                # Constructing an object
                try:
                    construct_me = Constructor()
                    
                    # Everything OK
                    return valid(construct_me)
                    
                # FAIL!
                except Exception as e:
                    return invalid(str(e)
                    
            # Some public method
            def im_public(self):
            
                # Call the internal method
                status = self._im_internal()
                
                # If the response is valid
                if not status['valid']:
                
                    # Return the error message. Any API objects calling this should know
                    # how to handle the dictionary response. Ultimately this gets passed
                    # back to the API request handler.
                    return status
                    
                # Get the constructed object
                some_obj = status['content']
                
    :param msg: An optional message or return content
    :type msg: str|list|dict|class|method
    :param data: Additional data that can be returned to the API client
    :type data: dict|list|str
    :rtype: dict
    """
    if not msg:
        return { 'valid': True, 'content': None , 'data': data }
    return { 'valid': True, 'content': msg , 'data': data }

def invalid(msg, code=400):
    """
    Similar to the 'valid' method in usage. Returns a dictionary with the 'valid' flag
    set to false. Can specify an optional HTTP return code. Takes an error message or 
    object as the first argument.
    
    :param msg: The error message or object
    :type msg: str|list|dict
    :param code: The HTTP response code, defaults to 400
    :type code: int
    :rtype: dict
    """
    return { 'valid': False, 'code': code, 'content': msg }

def format_action(a, m, w=10, b=False):
    """
    Simple helper method used to format action entries in the help prompt for the CloudScape
    agent.
    
    :param a: The action string
    :type a: str
    :param m: The action help message
    :type m: str
    :param w: The width of the action column
    :type w: int
    :param b: Use a carriage return in the output
    :type b: boolean
    :rtype: str
    """
    b = '' if not b else '\r'
    return "{0:<{1}}{2}{3}\n".format(a, w, m, b)

"""
Parse HTTP Response

Wrapper method to return a globally formatted object regardless of the syntactic differences
between versions of 'python-requests' on different Linux distributions.
"""
def parse_response(obj):
    """
    Helper method used to parse a Python requests object and return a formatted dictionary.
    Used to help alleviate differences between versions of the requests module on different
    systems.
    
    :param obj: The response object to parse
    :type obj: object
    :rtype: dict
    """
    return_obj = {}
    
    # Look for the status code
    if hasattr(obj, 'status_code'):
        return_obj['code'] = obj.status_code
    if hasattr(obj, 'code'):
        return_obj['code'] = obj.code
    
    # Look for the return body
    if hasattr(obj, 'content'):
        return_obj['body'] = obj.content
    if hasattr(obj, 'text'):
        if callable(getattr(obj, 'text')):
            return_obj['body'] = obj.text()
        else:
            return_obj['body'] = obj.text
    
    # Return the formatted response
    return return_obj

class UtilsBase(object):
    """
    Utilities base class for specific classes. Constucts the configuration and logging
    objects depending if you are on a server or agent.
    """
    def __init__(self, child):
        """
        Class constructor.
        
        :param child: Child class object
        :type child: class object
        """
    
        # Define the logger name
        log_name  = '%s.%s' % (__name__, child.__class__.__name__)

        # Running utilities on the server
        if os.path.isfile(S_CONF):
            self.conf = config.parse()
            self.log  = logger.create(log_name, self.conf.utils.log)
            
        # Agent Configuration
        elif (os.path.isfile(A_CONF)):
            self.conf = AgentConfig().get()
            self.log  = logger.create(log_name, self.conf.agent.log)
            
        # Raise an exception if neither the server nor agent configuration is found
        else:
            raise Exception('Could not locate the server or agent configuration')

class FileSec(UtilsBase):
    """
    File security class. Used to generate checksums, as well as encrypt and 
    decrypt files.
    """
    def __init__(self):
        super(FileSec, self).__init__(self)
        
        # File chunk size
        self.chunk_size = 64*1024
    
    def checksum(self, filename=None):
        """
        Generate and return a SHA256 checksum of a target file.
        
        Get a file checksum::
        
            # Import the utility and create an instance
            from cloudscape.common.utils import FileSec
            fs = FileSec()
            
            # Get the checksum of a file
            csum = fs.checksum('/path/to/file.txt')
        
        :param filename: The file name to checksum
        :type filename: str
        :rtype: str
        """
        if not filename or not os.path.isfile(filename):
            return False
        
        # Find the hash of the file
        hash_obj = hashlib.sha256(open(filename, 'rb').read())
        checksum = hash_obj.hexdigest()
        
        # Log and return the checksum
        self.log.info('Generating SHA256 checksum \'%s\' for: %s' % (checksum, filename))
        return checksum
    
    def encrypt(self, infile, outfile, key):
        """
        Encrypt a file using PyCrypto and an encryption key.
        
        Encrypt a file::
        
            # Import the utility and create an instance
            from cloudscape.common.utils import FileSec
            fs = FileSec()
            
            # Input and output file
            infile = '/some/file.txt'
            outfile = '/some/file.txt.enc'
            
            # Encryption key
            key = 'secret'
            
            # Encrypt a file
            fs.encrypt(infile, outfile, key)
        
        :param infile: The file to encrypt
        :type infile: str
        :param outfile: The encrypted file path
        :type outfile: str
        :param key: The encryption key
        :type key: str
        :rtype: boolean
        """
        if not os.path.isfile(infile):
            self.log.error('Failed to enrypt file [%s]: file not found' % infile)
            return False 
        if os.path.isfile(outfile):
            self.log.error('Failed to encrypt file - output file [%s] already exists' % outfile)
            return False
        
        # Encrypt the file
        iv        = b''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize  = os.path.getsize(infile)
        with open(infile, 'rb') as ifh:
            with open(outfile, 'wb') as ofh:
                ofh.write(struct.pack('<Q', filesize))
                ofh.write(iv)
                while True:
                    chunk = ifh.read(self.chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)
                    ofh.write(encryptor.encrypt(chunk))
        self.log.info('Encrypting file \'%s\' to \'%s\' using AES-256 and key string' % (infile, outfile))
        return True
    
    def decrypt(self, infile, outfile, key):
        """
        Decrypt a file using PyCrypto and an encryption key.
        
        Decrypt a file::
        
            # Import the utility and create an instance
            from cloudscape.common.utils import FileSec
            fs = FileSec()
            
            # Input and output file
            infile = '/some/file.txt.enc'
            outfile = '/some/file.txt'
            
            # Encryption key
            key = 'secret'
            
            # Decrypt a file
            fs.decrypt(infile, outfile, key)
        
        :param infile: The file to decrypt
        :type infile: str
        :param outfile: The decrypted file path
        :type outfile: str
        :param key: The encryption key
        :type key: str
        :rtype: boolean
        """
        if not os.path.isfile(infile):
            self.log.error('Failed to decrypt file [%s]: file not found' % infile)
            return False 
        if os.path.isfile(outfile):
            self.log.error('Failed to decrypt file - output file [%s] already exists' % outfile)
            return False
        
        # Decrypt the file
        with open(infile, 'rb') as ifh:
            origsize  = struct.unpack('<Q', ifh.read(struct.calcsize('Q')))[0]
            iv        = ifh.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)
            with open(outfile, 'wb') as ofh:
                while True:
                    chunk = ifh.read(self.chunk_size)
                    if len(chunk) == 0:
                        break
                    ofh.write(decryptor.decrypt(chunk))
                ofh.truncate(origsize)
        self.log.info('Decrypting file \'%s\' to \'%s\' using AES-256 and key string' % (infile, outfile))
        return True

class JSONTemplate(UtilsBase):
    """
    A utility class designed to validate a JSON object against a template file. Used
    to verify the structure of API requests, formula manifests, etc. For a full example
    of how to construct a JSON validation template, please see the files in:
    
    /opt/cloudscape/engine/templates/api
    """
    def __init__(self, template=None):
        super(JSONTemplate, self).__init__(self)
        
        # Set the template object
        self.template_obj = template

        # Template and target file objects
        self.template     = None
        self.target       = None

    def _is_type(self, var, type):
        """
        Helper method used to simplify testing for differen types of variables, as well
        as validating non-builtin Python types, such as UUID4, IPv4, etc.
        
        :param var: The variable to test
        :type var: str|list|dict|int|bool
        :param type: The type the variable should be
        :type type: str
        :rtype: boolean
        """
        if type == 'dict':
            if isinstance(var, dict):
                return True
            return False
        if type == 'list':
            if isinstance(var, list):
                return True
            return False
        if type == 'str':
            if isinstance(var, unicode) or isinstance(var, str) or isinstance(var, basestring):
                return True
            return False
        if type == 'int':
            if isinstance(var, int) or isinstance(var, float) or isinstance(var, long):
                return True
            return False
        if type == 'uuid4':
            try:
                v = uuid.UUID(var, version=4)
                return True
            except:
                return False
        if type == 'bool':
            if isinstance(var, bool):
                return True
            return False
        if type == '*':
            return True
    
    def _load_json(self, obj):
        """
        Helper method to load and validate basic JSON structure to see if it is
        syntactically correct.
        
        :param obj: The JSON object to validate
        :type obj: dict|list
        :rtype: valid|invalid
        """
        obj_valid = None
        if self._is_type(obj, str):
            try:
                obj_valid = json.loads(obj)
            except:
                return invalid('JSON string argument is not valid JSON')
        else:
            try:
                obj_tmp = json.dumps(obj)
                obj_valid = obj
            except:
                return invalid('JSON object argument is not valid JSON')
        return valid(obj_valid) 
    
    # Try to parse the tempalte and target objects
    def _parse_files(self, target_obj):
        
        # If either of the objects are not valid
        template_obj = self._load_json(self.template_obj)
        target_obj   = self._load_json(target_obj)
        if not template_obj['valid']:
            return template_obj['content']
        if not target_obj['valid']:
            return target_obj['content']
        
        # Load the validation objects
        self.template = template_obj['content']
        self.target   = target_obj['content']
    
    # Return path error
    def _formula_err(self, map, msg):
        fe_msg = 'Error at %s: %s' % (map, msg)
        self.log.error(fe_msg)
        return fe_msg
    
    # Validate a JSON file against the template
    def validate(self, target_str=None):
        parse_err = self._parse_files(target_str)
        if parse_err:
            return parse_err
        self.log.info('Validating target JSON string: %s' % target_str)

        # Set the parent object
        m = 'root'
        
        # Walk through a ditionary block
        # p:  Parent key
        # t:  Relative template block
        # f:  Relative formula block
        # m:  Current formula map
        # cb: Optional callblack function
        def _dict_walk(p,t,f,m,cb=None):
            
            # Walk through a list block
            # k: List block key
            # l: List object to walk through
            # t: Relative template object
            # m: Current formula map
            def _list_walk(k,l,t,m):
                c = 0
                for o in l:
                    
                    # If the list object is empty
                    if not o:
                        return self._formula_err(m, 'List object is empty')
                    
                    # Validate the list object type
                    ot = t['_type']
                    if not self._is_type(o,ot):
                        return self._formula_err(m, 'Invalid list object type')
                    
                    # Set the formula map
                    if c == 0:
                        m += '/%d' % c
                    else:
                        m = re.compile('(^.*\/%s\/)[0-9]*(.*$)' % k).sub(r'\g<1>%s\g<2>' % c, m)
                    
                    # Walk through nested items in the list
                    obj_err = _dict_walk(c,t,o,m)
                    if obj_err:
                        return obj_err
                    c += 1
            
            # Data type
            dt = t['_type']
            
            # Validate the data type of the current formula level
            if not self._is_type(f, dt):
                if ('_empty' in t) and (t['_empty'] == True):
                    pass
                else:
                    return self._formula_err(m, 'Object is an invalid type, should be %s' % dt)
            
            # If the current level has no children
            if not '_children' in t:
                
                # Look for the values flag
                if '_values' in t and self._is_type(t['_values'], 'list'):
                    if self._is_type(f, 'list'):
                        for fk in f:
                            if not fk in t['_values']:
                                return self._formula_err(m, 'Object value \'%s\' is not in supported values list: \'%s\'' % (fk, ', '.join(t['_values'])))
                    else:
                        if f not in t['_values']:
                            return self._formula_err(m, 'Object value \'%s\' is not in supported values list: \'%s\'' % (f, ', '.join(t['_values'])))
            
                # Look for the integer range flag
                if '_range' in t and self._is_type(f, 'str'):
                    b = re.compile('(^[^\/]*)\/[^\/]*$').sub(r'\g<1>', f)
                    e = re.compile('^[^\/]*\/([^\/]*$)').sub(r'\g<1>', f)
                    if not int(b) <= int(f) <= int(e):
                        return self._formula_err(m, 'Object value \'%s\' must be between \'%s\' and \'%s\'' % (f, b, e))
            
            # If the current level has children
            else:
                
                # Required and optional keys
                rk = t['_required']
                ok = t['_optional']
                
                # Make sure all required keys are set
                mkv = []
                rks = []
                for rkv in rk:
                    
                    # If processing a group of alternate key choices
                    if self._is_type(rkv, 'list'):
                        akf = False
                        for ak in rkv:
                            if ak in f:
                                akf = True
                                rks.append(ak)
                        if not akf:
                            mkv.append('(%s)' % '/'.join(rkv))
                        
                    # Make sure the key is set
                    else:
                        if not rkv in f:
                            mkv.append(rkv)
                        else:
                            rks.append(rkv)
                
                # If any required keys are missing
                if mkv:
                    return self._formula_err(m, 'Missing required key values: %s' % ', '.join(mkv))
                
                # Process the formula level
                for k,v in f.iteritems():
                    m += '/%s' % k
                    
                    # Check if the key is required, optional, or unsupported
                    wc = False
                    if not k in rks:
                        if not k in ok:
                            if not '*' in ok:
                                return self._formula_err(m, 'Using unsupported key \'%s\' without wildcard flag' % k)
                            
                            # Current key is a wildcard entry
                            else:
                                wc = True
                
                    # Set the next template object
                    try:
                        to = t['_children']['*'] if wc else t['_children'][k]
                    except:
                        continue
                    tt = to['_type']
                    
                    # If the current formula key contains a list
                    if tt == 'list' and '_contains' in to:
                        
                        # Walk through the list objects
                        tco  = to['_contains']
                        lerr = _list_walk(k,v,tco,m)
                        if lerr:
                            return lerr
                    
                    # If current formula level contains a dictionary
                    else:
                        
                        # Make sure the value is set and the data type is correct
                        if not v and not self._is_type(v,'int'):
                            if ('_empty' in to) and (to['_empty'] == True):
                                pass
                            else:
                                return self._formula_err(m, 'Value for key \'%s\' is not defined or empty' % k)
                        if not self._is_type(v,tt):
                            if ('_empty' in to) and (to['_empty'] == True):
                                pass
                            else:
                                return self._formula_err(m, 'Invalid data type for key \'%s\', expected \'%s\'' % (k,tt))
                         
                        # Walk through the next level of the formula
                        ferr = _dict_walk(p,to,f[k],m)
                        if ferr:
                            return ferr
                   
                    # Reset the formula map
                    if p == 'root':
                        m = p
                    else:
                        m = re.compile('(^.*)\/[^>]*$').sub(r'\g<1>', m)
            
            # Run the callback function
            if cb: cb()
                   
        # Recursive callback
        self.log.info('Initializing template validation run')
        def rcb():
            self.log.info('Completed template validation run')
                   
        # Walk through and validate the formula structure with the template
        return _dict_walk('root',self.template['root'],self.target,m,rcb)