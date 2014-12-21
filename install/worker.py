#!/usr/bin/python
import os
import re
import sys
import json
import shutil
import traceback
import importlib
from distutils import dir_util
from __builtin__ import False, True

# Load the feedback handler
from python.cloudscape.common.feedback import Feedback

class CloudScapeInstaller(object):
    """
    Class used to install CloudScape from GitHub sources.
    
    INSTALLATION NOTES:
    
    python-six: Needs to be at least version 1.6.x. Can be fixed using
    'pip install --upgrade six'.
    """
    def __init__(self):
    
        # These values should be user configurable
        self.base     = '/opt/cloudscape'
    
        # Feedback handler
        self.fb       = Feedback()
    
        # Load the installation manifest
        self.manifest = self._load_manifest()
    
        # Required modules and imports
        self.modules  = {}
    
    def _find_mod(self):
        
        # Store all imported modules
        imp_def  = {}
        from_def = {}
        
        for r,d,f in os.walk('python/cloudscape'):
            for _f in f:
                
                # Comment block marker
                is_comment = False
                
                # If scanning a regular Python file
                if re.match(r'^.*\.py$', _f):
                    file = '%s/%s' % (r, _f)
                    contents = open(file, 'r').read()

                    # If processing a multi-line import statement                    
                    is_from  = False
                    from_mod = None
                    is_imp   = False
                
                    # Process each file line
                    for l in contents.splitlines():
                        
                        # If processing a single line comment block
                        if re.match(r'^[ ]*"""[^"]*"""$', l):
                            continue
                        
                        # If processing a comment block
                        if is_comment:
                            if '"""' in l:
                                is_comment = False
                            continue    
                    
                        # If processing the opening of a comment block
                        if '"""' in l:
                            is_comment = True
                            continue
                    
                        # If processing a single line comment
                        if re.match(r'^[ ]*#.*$', l):
                            continue
                        
                        # If processing a multi-line import statement
                        if is_imp:
                            for i in l.strip().split(','):
                                is_imp = False if not '\\' in i else True
                        
                                if i.strip():
                                    if not i in imp_def:
                                        as_name = False
                                        m_name  = i.strip()
                                        if ' as ' in i:
                                            i_name  = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', i)
                                            as_name = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', i)
                                        if i != '\\':
                                            imp_def[i_name.replace('(', '').replace(')', '')] = as_name
                            continue
                        
                        # If processing a multi-line from statement
                        if is_from:
                            for f in l.strip().split(','):
                                is_from = False if not '\\' in f else True
                                
                                if not f in from_def[from_mod]:
                                    as_name  = False
                                    obj_name = f.strip()
                                    if ' as ' in f:
                                        obj_name = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', f)
                                        as_name  = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', f)
                                    if obj_name != '\\':
                                        from_def[from_mod][obj_name.replace('(', '').replace(')', '')] = as_name
                            continue
                        
                        # Look for either entire module or module object imports
                        imp_match = re.match(r'^import[ ]*.*$', l)
                        from_match = re.match(r'^from[ ]*.*$', l)
                        if imp_match or from_match:
                            
                            # If importing entire module(s)
                            if imp_match:
                                imp_mods = re.compile(r'^import[ ]*(.*$)').sub(r'\g<1>', l)
                                for m in imp_mods.split(','):
                                    
                                    # If continuing import statements on the next line
                                    if '\\' in m:
                                        is_imp = True
                                    
                                    if m.strip():
                                        if not m in imp_def:
                                            as_name = False
                                            m_name  = m.strip()
                                            if ' as ' in m:
                                                m_name  = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', m)
                                                as_name = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', m)
                                            imp_def[m_name.replace('(', '').replace(')', '')] = as_name
                                
                            # If importing specific objects from module(s)
                            if from_match:
                                from_regex = re.compile(r'^from[ ]*([^ ]*)[ ]*import[ ]*(.*$)')
                                from_mod   = from_regex.sub(r'\g<1>', l)
                                from_objs  = from_regex.sub(r'\g<2>', l)
                                
                                if not from_mod in from_def:
                                    from_def[from_mod] = {}
                                    
                                # Get each object being imported from the module
                                for _obj in from_objs.split(','):
                                    obj = _obj.strip()
                                    if not obj:
                                        continue
                                    
                                    # If continuing import statements on the next line
                                    if '\\' in obj:
                                        is_from = True
                                    
                                    if not obj in from_def[from_mod]:
                                        as_name  = False
                                        obj_name = obj.strip()
                                        if ' as ' in obj:
                                            obj_name = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', obj)
                                            as_name  = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', obj)
                                        if obj_name != '\\':
                                            from_def[from_mod][obj_name.replace('(', '').replace(')', '')] = as_name
    
        # Set the required imports objects
        self.modules = { 'import': imp_def, 'from': from_def }
    
    def _import_wrapper(self, mod):
        try:
            i = importlib.import_module(mod)
            self.fb.show('Discovered module [%s]' % mod).success()
            return i
        except Exception as e:
                self.fb.show('Failed to import required module [%s]: %s' % (mod, str(e))).error()
                traceback.print_exc()
                sys.exit(1)
        
    def _skip_import(self, mod):
        
        # Skip Windows agent modules
        if re.match(r'cloudscape\.agent\.win.*$', mod):
            return True
        
        # Skip explicity ignored modules
        if mod in self.manifest['modules']['ignore']:
            return True
        
    def _try_import(self):
        self.fb.show('Checking for required modules and objects...').info()
        
        for o,a in self.modules['import'].iteritems():
            if self._skip_import(o):
                continue
            
            # Make sure the module is available
            self._import_wrapper(o)
            
        for f,o in self.modules['from'].iteritems():
            if self._skip_import(f):
                continue
            
            # Make sure the module is available
            self._import_wrapper(f)
    
    def _load_manifest(self):
        if not os.path.isfile('manifest.json'):
            self.fb.show('Missing installation manifest file [manifest.json]').error()
            sys.exit(1)
        self.fb.show('Discovered installation manifest file [manifest.json]').success()
    
        try:
            _manifest = json.loads(open('manifest.json', 'r').read())    
            self.fb.show('Parsed installation manifest file [manifest.json]').success()
            return _manifest
        except Exception as e:
            self.fb.show('Failed to parse manifest file [manifest.json]: %s' % str(e)).error()
            sys.exit(1)
    
    def _mkdir(self, path):
        try:
            os.mkdir(path)
        except:
            return
    
    def _copy_local(self):
        self.fb.show('Copying CloudScape files to installation directory [%s]' % self.base).info()
        
        # Make sure the base directory is available
        if os.path.isdir(self.base):
            self.fb.show('CloudScape base directory [%s] already exists' % self.base).error()
            sys.exit(1)
        self._mkdir(self.base)
                
        # Copy folders
        for f in self.manifest['folders']:
            try:
                dir_util.copy_tree(f, '%s/%s' % (self.base, f))
                self.fb.show('Copying directory [%s] to [%s/%s]' % (f, self.base, f)).success()
            except Exception as e:
                self.fb.show('Failed to copy directory [%s] to [%s/%s]: %s' % (f, self.base, f, str(e))).error()
                sys.exit(1)
            
        # Copy files
        for f in self.manifest['files']:
            try:
                shutil.copyfile(f, '%s/%s' % (self.base, f))
                self.fb.show('Copying file [%s] to [%s/%s]' % (f, self.base, f)).success()
            except Exception as e:
                self.fb.show('Failed to copy file [%s] to [%s/%s]: %s' % (f, self.base, f, str(e))).error()
                sys.exit(1)

    def _symlinks(self):
        self.fb.show('Creating system links...').info()
        for l in self.manifest['links']:
            src = '%s/_local%s' % (self.base, l)
            dst = l
            try:
                os.symlink(src, dst)
                self.fb.show('Created system link [%s] -> [%s]' % (src, dst)).success()
            except Exception as e:
                self.fb.show('Failed to create system link [%s] -> [%s]: %s' % (src, dst, str(e))).error()
                sys.exit(1)

    def _init_config(self):
        
        # Default and user defined configuration files
        def_config = '%s/conf/default/server.conf' % self.base
        usr_config = '%s/conf/server.conf' % self.base
        
        # Create the user defined configuration file
        shutil.copyfile(def_config, usr_config)
        self.fb.show('Initialized server configuration [%s] -> [%s]' % (def_config, usr_config)).success()

    def _init_dbkeys(self):
        
        # Database encryption key
        dbkey = '/opt/cloudscape/dbkey'
        
        # Attempt to create database encryption keys
        try:
            os.system('keyczart create --location=/opt/cloudscape/dbkey --purpose=crypt')
            os.system('keyczart addkey --location=/opt/cloudscape/dbkey --status=primary --size=256')
            self.fb.show('Created database encryption keys in: %s' % dbkey)
        except Exception as e:
            self.fb.show('Failed to create database encryption keys: %s' % str(e)).error()
            sys.exit(1)

    def _init_log(self):
        
        # Default log directory
        log_dir = '/var/log/cloudscape'
        dir_util.mkpath(log_dir)

    def _set_env(self):
        
        # CloudScape base path
        os.environ['CLOUDSCAPE_BASE'] = self.base
        
        # Django settings module
        os.environ['DJANGO_SETTINGS_MODULE'] = 'cloudscape.engine.api.core.settings'
        
        # Make Python modules accessible
        sys.path.append('%s/python' % self.base)
        self.fb.show('Appended [%s/python] to Python path' % self.base).success()

    def _deploy(self):
        
        # Deployed flag
        df = 'tmp/deployed'
        
        # If the software has already been deployed
        if os.path.isfile(df):
            self.fb.show('Software deployment already completed, skipping...').info()
            return
        
        # Deploy software and setup the environment
        self._copy_local()
        self._symlinks()
        self._init_config()
        self._init_dbkeys()
    
        # Software deployed
        dh = open(df, 'w')
        dh.close()
    
    def _install(self):
        self._set_env()
        self._find_mod()
        self._try_import()

    def run(self):
        
        # Valid installation arguments
        args = {
            'deploy': {
                'help':   '',
                'method': self._deploy
            },
            'install': {
                'help':   '',
                'method': self._install
            }
        }
        
        # Make sure an argument is supplied
        if not len(sys.argv == 2) or not (sys.argv[1] in args):
            print 'Missing or invalid argument: [%s]\n' % sys.argv[1]
            print 'Supported arguments are:'
            for a,p in args.iteritems():
                print '> %s: %s' % (a,p['help'])
            print '\n'
            sys.exit(1)
        
        # Run the installation step
        self._run[sys.argv[1]]()
    
if __name__ == '__main__':
    installer = CloudScapeInstaller()
    installer.run()