import json
import base64
from collections import OrderedDict

# Lense Libraries
from lense.common import config
from lense.common import logger

class APIFilter(object):
    """
    Class container for API response filters.
    """
    def __init__(self):
        
        # Target filter object / filter map
        self._object = None
        self._map    = {}
    
        # Configuration / logger
        self.conf    = config.parse('PORTAL')
        self.log     = logger.create(__name__, self.conf.portal.log)
        
    def object(self, obj):
        """
        Set the data object to filter.
        """
        
        # Set the internal object container
        self._object = obj
        
        # Return the class
        return self
    
    def map(self, key):
        """
        Map API request paths to any supported filters.
        """
        
        # If a filter is supported
        if (key in self._map) and callable(self._map[key]):
            self._map[key]()
            
        # Return the object
        return self._object