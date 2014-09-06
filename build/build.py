#!/usr/bin/python

#%{name}-%{major}.%{minor}.el6.%{arch}

from __future__ import print_function
import os
import re
import sys
import json
import errno
import shutil
from deb_pkg_tools.package import build_package

class Builder(object):
    """
    Convenience script for generating *.deb packages for all the CloudScape
    server and client components.
    """
    def __init__(self):
    
        # Target component / available components
        self.target = None
        self.components = {}
    
        # Find available packages
        self._find_components()
    
    def _construct_path(self, path):
        """
        Construct the parent directory of a given path.
        """
        parent = re.compile(r'(^.*)[\/|\\][^\/|\\]*$').sub(r'\g<1>', path)
        self._mkdir(parent)
    
    def _mkdir(self, dir):
        """
        Convenience method for creating a directory.
        """
        try:
            print('Creating directory: %s' % dir)
            os.makedirs(dir)
        except:
            pass
    
    def _rm(self, path):
        """
        Convenience method for removing a directory or file.
        """
        try:
            os.remove(path)
        except:
            try:
                shutil.rmtree(path)
            except:
                pass
    
    def _cp(self, src, dst):
        """
        Convenience method for copying files and directories.
        """
        try:
            print('Copying contents: %s -> %s' % (src, dst))
            shutil.copytree(src, dst)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: 
                return False
    
    def _build_pkg_root(self, root, sources):
        """
        Construct the package root.
        """
    
        # Begin processing each source entry
        for s in sources:
            build_path = '%s%s' % (root, s)
            self._construct_path(build_path)
            self._cp(s, build_path)
    
    def _create_control_file(self, component, root, manifest):
        """
        Generate a control file.
        """
        print('Generating control file')
        
        # Read the control file into a string
        control_file = open('%s/control' % component, 'r').read()
        dest_file = '%s/DEBIAN/control' % root
    
        # Update the major / minor / release placeholders
        control_file = control_file.replace('$MAJOR', str(manifest['major'])).replace('$MINOR', str(manifest['minor'])).replace('$RELEASE', str(manifest['release']))
    
        # Create the DEBIAN directory
        self._construct_path(dest_file)
        
        # Generate the control file
        print('Generating control file: %s' % dest_file)
        file_handle = open(dest_file, 'w')
        file_handle.write(control_file)
        file_handle.close()
    
    def _cleanup(self):
        """
        Remove the temporary directory.
        """
        self._rm('tmp')
    
    def _copy_scripts(self, component, root):
        """
        Copy any installation/removal scripts.
        """
        files = ['postinst', 'preinst', 'prerm', 'postrm']
        for file in files:
            src_script = '%s/%s' % (component, file)
            dst_script = '%s/DEBIAN/%s' % (root, file)
            if os.path.isfile(src_script):
                self._cp(src_script, dst_script)
                os.system('chmod +x %s' % dst_script)
    
    def _build(self, component, manifest):
        """
        Worker method for building a single component.
        """
        
        # Store the major / minor / release values
        major = manifest['major']
        minor = manifest['minor']
        release = manifest['release']
        
        print('Preparing to package component: %s' % component)
        print('Generating new release: %s.%s-%s -> %s.%s-%s' % (major, minor, release, major, minor, (release + 1)))
    
        # Update the manifest release value
        manifest['release'] = release + 1
        
        # Construct the package build root
        build_root = 'tmp/%s_%s.%s-%s' % (component, major, minor, manifest['release'])
        self._build_pkg_root(build_root, manifest['source'])
    
        # Generate the control file
        self._create_control_file(component, build_root, manifest)
    
        # Copy any extra scripts
        self._copy_scripts(component, build_root)
    
        # Build the package
        build_package(build_root, copy_files=False, repository='output')
    
        print('Successfully built component "%s" package: %s_%s.%s-%s.deb' % (component, component, major, minor, manifest['release']))
    
        # Update the manifest
        print('Updating release in manifest')
        with open('manifest/%s' % component, 'w') as handle:
            json.dump(manifest, handle)
    
    def _find_components(self):
        """
        Look for package manifests.
        """
        
        # Required component keys
        required_keys = ['major', 'minor', 'release', 'source']
        
        # Make sure the component manifest directory exists
        if not os.path.isdir('manifest'): 
            print('Missing required "manifest" directory')
            sys.exit(1)
        
        # Load every manifest
        for root,dirs,files in os.walk('manifest'):
            for component in files: 
                
                # Make sure the manifest has a relative control file
                if not os.path.isfile('%s/control' % component):
                    print('Missing required control file for "%s" component' % component) 
                    sys.exit(1)
    
                # Load the component manifest
                try:
                    manifest = json.load(open('manifest/%s' % component, 'r'))
                
                # Failed to read the component manifest
                except Exception as e:
                    print('Failed to read manifest for "%s" component: %s' % (component, str(e))) 
                    sys.exit(1)
                
                # Make sure the required keys are set
                for k in required_keys:
                    if not k in manifest:
                        print('%s: Missing required key "%s" in "%s" manifest' % (component, k)) 
                        sys.exit(1)
                
                # Make sure the major / minor / release attributes are integers
                for k in ['major', 'minor', 'release']:
                    if not isinstance(manifest[k], int):
                        print('%s: Manifest key "%s" must be an integer' % (component, k))
                        sys.exit(1)
                
                # Make sure all the sources exist
                for s in manifest['source']:
                    if not os.path.isfile(s) and not os.path.isdir(s):
                        print('%s: Source entry "%s" is not a valid file or directory' % (component, s)) 
                        sys.exit(1)
                
                # Load in the the components object
                self.components[component] = manifest
    
    def launch(self):
        """
        Launch the build utility.
        """
        
        # Make sure a build target is specified
        if not len(sys.argv) > 1:
            print('Must either run either "build all" or "build <component>"') 
            sys.exit(1)
            
        # Store the build target
        self.target = sys.argv[1]
        
        # Make sure the target is valid
        if not (self.target == 'all') and not (self.target in self.components):
            print('Invalid target component "%s", must be "all" or one of: %s' % (self.target, ', '.join(self.components.keys()))) 
            sys.exit(1)
            
        # If building all
        if self.target == 'all':
            for c,m in self.components.iteritems():
                self._build(c,m)
             
        # Build a single component   
        else:
            self._build(self.target, self.components[self.target])
    
        # Cleanup
        self._cleanup()
    
if __name__ == '__main__':
    Builder().launch()