#!/usr/bin/python
import os
import re
import apt
import sys
import json
import shutil
import traceback
import importlib
from distutils import dir_util
from __builtin__ import False, True  

# Installation libraries
from lib.db import CloudScapeDatabase
from lib.util import CloudScapeUtils
from lib.config import CloudScapeConfig
from lib.apache import CloudScapeApache
from lib.nodejs import CloudScapeNodeJS
from lib.modules import CloudScapeModules

# Installer utilities
UTIL = CloudScapeUtils()
CONF = CloudScapeConfig().construct()

class CloudScapeInstaller(object):
    """
    Class used to install CloudScape from GitHub sources.
    
    INSTALLATION NOTES:
    
    python-six: Needs to be at least version 1.6.x. Can be fixed using
    'pip install --upgrade six'.
    """
    def __init__(self):
    
        # Installation manifest
        self.manifest = None
    
        # Installation utilities
        self.db = CloudScapeDatabase(CONF)
    
        # Set up logging
        self._bootstrap_log()
    
        # Required modules and imports
        self.modules  = CloudScapeModules().construct()
    
    def _bootstrap_log(self):
        _log_dir = '/var/log/cloudscape'
        _log_file = '%s/server.log' % _log_dir
        
        if not os.path.isdir(_log_dir):
            os.mkdir(_log_dir)
        if not os.path.isfile(_log_file):
            open(_log_file, 'a')
    
    def _import_wrapper(self, mod):
        try:
            i = importlib.import_module(mod)
            UTIL.fb.show('Discovered module [%s]' % mod).success()
            return i
        except Exception as e:
                UTIL.fb.show('Failed to import required module [%s]: %s' % (mod, str(e))).error()
                traceback.print_exc()
                sys.exit(1)
        
    def _skip_import(self, mod):
        
        # Skip Windows agent modules
        if re.match(r'cloudscape\.agent\.win.*$', mod):
            return True
        
        # Skip explicity ignored modules
        if mod in self.manifest['modules']['ignore']:
            return True
        
    def _install_apt(self):
        cache = apt.cache.Cache()
        cache.update()
        for pkg in self.manifest['packages']['apt']:
            pkg = cache[pkg_name]   
            if pkg.is_installed:
                UTIL.fb.show('apt: Package "%s" already installed' % pkg_name).info()
            else:
                pkg.mark_install()

                try:
                    cache.commit()
                    UTIL.fb.show('apt: Package "%s" successfully installed' % pkg_name).success()
                except Exception as e:
                    UTIL.fb.show('apt: Failed to install package "%s"' % pkg_name).error()
                    sys.exit(1)
        
    def _install_pip(self):
        import pip
        pip.main(['install', self.manifest['packages']['pip']])
        
    def _try_import(self):
        UTIL.fb.show('Checking for required modules and objects...').info()
        
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
    
        # All modules discovered
        UTIL.fb.show('All required modules discovered in system Python path!').success()
    
    def _load_manifest(self):
        if not os.path.isfile('manifest.json'):
            UTIL.fb.show('Missing installation manifest file [manifest.json]').error()
            sys.exit(1)
        UTIL.fb.show('Discovered installation manifest file [manifest.json]').success()
    
        try:
            _manifest = json.loads(open('manifest.json', 'r').read())    
            UTIL.fb.show('Parsed installation manifest file [manifest.json]').success()
            return _manifest
        except Exception as e:
            UTIL.fb.show('Failed to parse manifest file [manifest.json]: %s' % str(e)).error()
            sys.exit(1)
    
    def _mkdir(self, path):
        try:
            os.mkdir(path)
        except:
            return
    
    def _copy_local(self):
        UTIL.fb.show('Copying CloudScape files to installation directory [%s]' % CONF.paths.base).info()
        
        # Make sure the base directory is available
        if os.path.isdir(CONF.paths.base):
            UTIL.fb.show('CloudScape base directory [%s] already exists' % CONF.paths.base).error()
            sys.exit(1)
        self._mkdir(CONF.paths.base)
                
        # Copy folders
        for f in self.manifest['folders']:
            _f = '../%s' % f
            try:
                dir_util.copy_tree(_f, '%s/%s' % (CONF.paths.base, f))
                UTIL.fb.show('Copying directory [%s] to [%s/%s]' % (f, CONF.paths.base, f)).success()
            except Exception as e:
                UTIL.fb.show('Failed to copy directory [%s] to [%s/%s]: %s' % (f, CONF.paths.base, f, str(e))).error()
                sys.exit(1)
            
        # Copy files
        for f in self.manifest['files']:
            _f = '../%s' % f
            try:
                shutil.copyfile(_f, '%s/%s' % (CONF.paths.base, f))
                UTIL.fb.show('Copying file [%s] to [%s/%s]' % (f, CONF.paths.base, f)).success()
            except Exception as e:
                UTIL.fb.show('Failed to copy file [%s] to [%s/%s]: %s' % (f, CONF.paths.base, f, str(e))).error()
                sys.exit(1)

    def _symlinks(self):
        UTIL.fb.show('Creating system links...').info()
        for l in self.manifest['links']:
            src = '%s/_local%s' % (CONF.paths.base, l)
            dst = l
            try:
                os.symlink(src, dst)
                UTIL.fb.show('Created system link [%s] -> [%s]' % (src, dst)).success()
            except Exception as e:
                UTIL.fb.show('Failed to create system link [%s] -> [%s]: %s' % (src, dst, str(e))).error()
                sys.exit(1)

    def _init_config(self):
        
        # Default and user defined configuration files
        def_config = '%s/conf/default/server.conf' % CONF.paths.base
        usr_config = '%s/conf/server.conf' % CONF.paths.base
        
        # Create the user defined configuration file
        shutil.copyfile(def_config, usr_config)
        UTIL.fb.show('Initialized server configuration [%s] -> [%s]' % (def_config, usr_config)).success()

    def _init_dbkeys(self):
        
        # Attempt to create database encryption keys
        try:
            os.system('keyczart create --location=%s --purpose=crypt' % CONF.paths.dbkey)
            os.system('keyczart addkey --location=%s --status=primary --size=256' % CONF.paths.dbkey)
            UTIL.fb.show('Created database encryption keys in: %s' % CONF.paths.dbkey)
        except Exception as e:
            UTIL.fb.show('Failed to create database encryption keys: %s' % str(e)).error()
            sys.exit(1)

    def _init_log(self):
        
        # Default log directory
        dir_util.mkpath(CONF.paths.log)

    def _set_env(self):
        
        # CloudScape base path
        os.environ['CLOUDSCAPE_BASE'] = CONF.paths.base
        
        # Django settings module
        os.environ['DJANGO_SETTINGS_MODULE'] = 'cloudscape.engine.api.core.settings'
        
        # Make Python modules accessible
        sys.path.append('%s/python' % CONF.paths.base)
        UTIL.fb.show('Appended [%s/python] to Python path' % CONF.paths.base).success()

    def _deploy(self):
        
        # Enable access to CloudScape modules prior to deployment
        self._load_mods()
        
        # Deployed flag
        df = 'tmp/deployed'
        
        # If the software has already been deployed
        if os.path.isfile(df):
            UTIL.fb.show('Software deployment already completed, skipping...').info()
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
        self._install_apt()
        self._install_pip()
        
        # Load CloudScape modules
        self._load_mods()
        
        self._set_env()
        self._try_import()

        # Setup the database
        self.db.setup()

    def run(self):
        
        # Load the manifest
        self.manifest = self._load_manifest()
        
        # Valid installation arguments
        args = {
            'deploy': {
                'help':   'Deploy CloudScape files and configure the environment and libraries',
                'method': self._deploy
            },
            'install': {
                'help':   'Run the installation script to bootstrap the CloudScape environment',
                'method': self._install
            }
        }
        
        # Make sure an argument is supplied
        if not (len(sys.argv) == 2) or not (sys.argv[1] in args):
            print '\nworker.py: Missing or invalid argument: [%s]\n' % 'none' if not (len(sys.argv) == 2) else sys.argv[1]
            print 'Supported arguments are:'
            for a,p in args.iteritems():
                print '> %s: %s' % (a,p['help'])
            print ''
            sys.exit(1)
        
        # Run the installation step
        args[sys.argv[1]]['method']()
    
if __name__ == '__main__':
    installer = CloudScapeInstaller()
    installer.run()