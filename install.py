#!/usr/bin/python
import os
import json
import shutil

class CloudScapeInstaller(object):
    """
    Class used to install CloudScape from GitHub sources.
    """
    def __init__(self):
    
        # Load the installation manifest
        self.manifest = self._load_manifest()
    
        # These values should be user configurable
        self.base = '/opt/cloudscape'
    
    def _load_manifest(self):
        if not os.path.isfile('manifest.json'):
            raise Exception('Missing installation manifest file [manifest.json]')
    
        try:
            return json.loads(open('manifest.json', 'r').read())    
        except Exception as e:
            raise Exception('Failed to parse manifest file [manifest.json]: %s' % str(e))
    
    def _mkdir(self, path):
        try:
            os.mkdir(path)
        except:
            return
    
    def _copy_local():
        
        # Make sure the base directory is available
        if os.path.isdir(self.base):
            raise Exception('CloudScape base directory [%s] already exists' % self.base)
        self._mkdir(self.base)
                
        # Copy folders
        for f in self.manifest['folders']:
            shutil.copytree(f, self.base)
            
        # Copy files
        for f in self.manifest['files']:
            shutil.copyfile(f, self.base)
                
    def run(self):
        self._copy_local()
    
if __name__ == '__main__':
    installer = CloudScapeInstaller()
    installer.run()