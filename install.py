#!/usr/bin/python
import os
import re
import sys
import json
import shutil
import importlib
from distutils import dir_util
from __builtin__ import False

# Load the feedback handler
from python.cloudscape.common.feedback import Feedback

class CloudScapeInstaller(object):
    """
    Class used to install CloudScape from GitHub sources.
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
    
    def _try_import(self):
        self.fb.show('Checking for required modules and objects...').info()
        for o,a in self.modules['import'].iteritems():
            try:
                importlib.import_module(o)
                self.fb.show('Located module [%s]' % o).success()
            except Exception as e:
                self.fb.show('Failed to locate required module [%s]: %s' % (o, str(e))).error()
                sys.exit(1)
            
        for f,o in self.modules['from'].iteritems():
            try:
                mod = importlib.import_module(f)
            except Exception as e:
                self.fb.show('Failed to locate required module [%s]: %s' % (f, str(e))).error()
                sys.exit(1)
                
            for _o,a in o.iteritems():
                if not hasattr(mod, _o):
                    self.fb.show('Module [%s] has no object [%s]' % (mod, _o)).error()
                    sys.exit(1)
    
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

    def run(self):
        self._copy_local()
        self._symlinks()
        self._find_mod()
        self._try_import()
    
if __name__ == '__main__':
    installer = CloudScapeInstaller()
    installer.run()