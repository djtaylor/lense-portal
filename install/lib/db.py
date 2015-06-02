import MySQLdb

# Installation libraries
from lib.util import CloudScapeUtils

class CloudScapeDatabase(object):
    def __init__(self, conf):
        self.conf = conf
        
        # Connection attributes
        self._db = {
            'host': None,
            'port': None,
            'user': None,
            'pass': None,
            'name': 'cloudscape'
        }
        
        # Database connection
        self._dbc = None
        
    def _connect(self):
        return
        
    def setup(self):
        
        # Open a database connection
        self._connect()