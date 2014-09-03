import copy
from collections import OrderedDict

# Django Libraries
from django.conf import settings
from django.db import connections

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common import config
from cloudscape.engine.api.app.host.models import DBHostDetails

# Maximum Rows per Table
MAX_ROWS = 360

class DBHostStats:
    """
    Main database model for storing polling statistics for managed hosts. Each host has its own
    table in the host statistics database.
    """
    def __init__(self, uuid=None):
        self.uuid    = uuid
        self.db      = settings.DATABASES['host_stats']
        self.dbh     = connections['host_stats'].cursor()

        # Configuration and logger
        self.conf    = config.parse()
        self.log     = logger.create(__name__, self.conf.server.log)

        # Parameters validation flag
        self.pv      = True

        # Create an ordered dictionary for the column names
        self.columns = OrderedDict([
            ('uptime',     'VARCHAR(48)'),
            ('cpu_use',    'TEXT'),
            ('memory_use', 'TEXT'),
            ('memory_top', 'TEXT'),
            ('disk_use',   'TEXT'),
            ('disk_io',    'TEXT'),
            ('network_io', 'TEXT')])

        # Make sure a UUID is specified
        if not self.uuid:
            self.pv = False

        # Make sure the UUID is mapped to an existing host
        if not DBHostDetails.objects.filter(uuid=self.uuid).count():
            self.pv = False

    def _table_init(self):
        """
        Initialize the host statistics table.
        """
        
        # Construct the columns string
        col_str = ''
        for name, data_type in self.columns.iteritems():
            col_str += ',%s %s' % (name, data_type)
        
        # Construct the table query
        timestamp  = 'created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        init_query = 'CREATE TABLE IF NOT EXISTS `%s`.`%s`(%s%s)' % (self.db['NAME'], self.uuid, timestamp, col_str)
        
        # Create the table
        try:
            self.dbh.execute(init_query)
            self.log.info('Initialized host \'%s\' statistics table' % self.uuid)
            return True
        except Warning:
            return True
        except Exception as e:
            self.log.error('Failed to initialize host \'%s\' statistics table: %s' % (self.uuid, e))
            return False
           
    def _construct_poll_query(self, params):
        """
        Construct the polling data column query.
        """
        col_names  = ''
        col_values = ''
        
        for key, data_type in self.columns.iteritems():
            col_names  += '%s,' % key
            col_values += '\'%s\',' % params[key]
        col_names  = col_names[:-1]
        col_values = col_values[:-1]
        
        # Construct and return the poll query
        return 'INSERT INTO `%s`.`%s`(%s) VALUES(%s)' % (self.db['NAME'], self.uuid, col_names, col_values)
      
    def _fetch_all(self, cursor):
        """
        Retrieve all rows from a raw SQL query.
        """
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        
    def _count(self):
        """
        Count the number of statistic rows being returned.
        """
        self.dbh.execute('SELECT COUNT(*) FROM `%s`' % self.uuid)
        result = self.dbh.fetchone()
        return result[0] 
        
    def get(self, range=None, latest=None):
        """
        Retrieve host statistics.
        """
        
        # If getting the latest N rows
        if latest:
            query = 'SELECT * FROM `%s`.`%s` ORDER BY created DESC LIMIT %s' % (self.db['NAME'], self.uuid, latest)
            self.dbh.execute(query)
            rows = self._fetch_all(self.dbh)
            
            # If returning a single row
            if latest == 1:
                return rows[0]
            else:
                return rows
        
        # If provided a start/end range
        if not 'start' in range or not 'end' in range:
            return False
        
        # Default range - last 60 entries
        if not range['start'] and not range['end']:
            query = 'SELECT * FROM `%s`.`%s` ORDER BY created DESC LIMIT 30' % (self.db['NAME'], self.uuid)
            
        # Select all up until end
        elif not range['start'] and range['end']:
            query = 'SELECT * FROM `%s`.`%s` WHERE created < \'%s\'' % (self.db['NAME'], self.uuid, range['end'])
            
        # Select from start date to end
        elif range['start'] and not range['end']:
            query = 'SELECT * FROM `%s`.`%s` WHERE created > \'%s\'' % (self.db['NAME'], self.uuid, range['start'])
            
        # Select between two date ranges
        else:
            query = 'SELECT * FROM `%s`.`%s` WHERE (created BETWEEN \'%s\' AND %s)' % (self.db['NAME'], self.uuid, range['start'], range['end'])
            
        # Select host statistics
        try:
            
            # Get the unsorted results
            self.dbh.execute(query)
            rows = self._fetch_all(self.dbh)
            
            # Convert to a dictionary with date as the key
            results_dict = {}
            for row in rows:
                key   = row['created'].strftime('%Y-%m-%d %H:%M:%S')
                stats = copy.copy(row)
                del stats['created']
                results_dict[row['created']] = stats
            
            # Order the dictionary by date
            results_sort = OrderedDict()
            for key, value in sorted(results_dict.iteritems(), key=lambda t: t[0]):
                results_sort[key] = value
                
            # Return the ordered resuls
            return results_sort
        except Exception as e:
            self.log.error('Failed to retrieve host statistics for \'%s\': %s' % (self.uuid, e))
            return False
            
    def create(self, params):
        """
        Create a new host statistics row.
        """
        
        # If any parameters are invalid
        if self.pv == False:
            self.log.error('Host UUID \'%s\' is invalid or is not a managed host' % self.uuid)
            return False
        
        # Require a row parameters dictionary
        if not params or not isinstance(params, dict):
            self.log.error('Missing required dictionary of column names/values')
            return False
        
        # Make sure all required 
        for key, data_type in self.columns.iteritems():
            if key not in params:
                self.log.error('Missing required column key \'%s\'' % key)
                return False

        # Make sure the host table exists
        table_status = self._table_init()
        if table_status != True:
            return False
        
        # Construct the polling query
        poll_query = self._construct_poll_query(params)
        
        # Create the statistics row
        try: 
            self.dbh.execute(poll_query)
            return True
        except Exception as e:
            self.log.error('Failed to create statistics row for host \'%s\': ' % (self.uuid, e))
            return False

    def delete(self):
        """
        Delete a host statistics table.
        """
        
        # If any parameters are invalid
        if self.pv == False:
            return False
        
        # Construct the drop table syntax
        drop_query = 'DROP TABLE IF EXISTS `%s`.`%s`' % (self.db['NAME'], self.uuid)
        
        # Drop the host statistics table
        try:
            self.dbh.execute(drop_query)
            return True
        except Exception as e:
            self.log.error('Failed to delete host \'%s\' statistics table: %s' % (self.uuid, e))
            return False