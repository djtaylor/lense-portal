import json
import base64
from collections import OrderedDict

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger

class APIFilter(object):
    """
    Class container for API response filters.
    """
    def __init__(self):
        
        # Target filter object / filter map
        self._object = None
        self._map    = self._construct_map()
    
        # Configuration / logger
        self.conf    = config.parse()
        self.log     = logger.create(__name__, self.conf.portal.log)
    
    def _construct_map(self):
        """
        Construct and return the filter map.
        """
        return {
            'host.get':         self._host_get,
            'host.get_formula': self._host_get_formula,
            'editor.get':       self._editor_get,
            'host.get_dkey':    self._host_get_dkey
        }
    
    def _unpack_host_firewall(self, firewall):
        """
        Format and sort host firewall information.
        """
        
        # Firewall columns
        columns = (
            ['src', 'Src'],
            ['dst', 'Dest'],
            ['protocol', 'Proto'],
            ['dport', 'DestPort'],
            ['sport', 'SrcPort'],
            ['in_interface', 'Interface'],
            ['state', 'State'],
            ['target', 'Target']
        )
        
        # Default tables
        tables_def = ['INPUT', 'OUTPUT', 'FORWARD']
        
        # Column defaults
        column_def = {
            'dport': 'any',
            'sport': 'any',
            'in_interface': 'any',
            'protocol': 'ip',
            'src': '0.0.0.0/0.0.0.0',
            'dst': '0.0.0.0/0.0.0.0'
        }
        
        # Sort the firewall tables
        firewall_sorted = sorted(firewall['config'].items(), key=lambda x: int(x[0]))
        
        # Sort the rules in each table
        for chain in firewall_sorted:
            
            # If the chain has a default policy
            if 'policy' in chain[1]:
                n = len(chain[1]['rules']) + 2
                chain[1]['rules'][str(n)] = { 'target': chain[1]['policy']}
                
            # Process each rule in the chain
            for n, rule in sorted(chain[1]['rules'].items(), key=lambda x: int(x[0])):
                rule_sorted = OrderedDict()
                
                # Set the value for each rule property column
                for column in columns:
                    if not column[0] in rule:
                        rule_sorted.update({column[0]: '' if not (column[0] in column_def) else column_def[column[0]]})
                    else:
                        rule_sorted.update({column[0]: rule[column[0]]})
                chain[1]['rules'][n] = rule_sorted
                
            # Sort the rules in the chain
            chain[1]['rules'] = sorted(chain[1]['rules'].items(), key=lambda x: int(x[0]))
            
        # Rebuild the firewall data
        firewall['config']    = firewall_sorted
        firewall['cols']      = columns
        firewall['deftables'] = tables_def
        
    def _unpack_host_formula_log(self, formula):
        """
        Unpack and sort a host formula log.
        """
        
        # If the log is empty
        if not formula['log']: return
        
        # Extract the log object
        log_json = json.loads(base64.b64decode(formula['log']))
            
        # Look for tracebacks and split lines
        for n,entry in log_json['log'].iteritems():
            if entry['type'] == 'EXCEPTION':
                log_json['log'][n]['traceback'] = log_json['log'][n]['traceback'].split('\n')
                
        # Sort the log items by entry number
        log_sorted = sorted(log_json['log'].items(), key=lambda x: int(x[0]))
        
        # Update the formula log entry
        log_json['log'] = log_sorted
        formula['log']  = log_json
        
    def _unpack_host(self, host):
        """
        Unpack host attributes.
        """
        
        # If the host has stored firewall information
        if ('firewall' in host['sys']) and (host['sys']['firewall']):
            self._unpack_host_firewall(host['sys']['firewall'])
        
    def _editor_get(self):
        """
        Filter formula editor content responses.
        """
        
        # Unpack the manifest
        self._object['manifest'] = json.loads(base64.decodestring(self._object['manifest']))
        
    def _host_get_dkey(self):
        """
        Filter host deployment key responses.
        """
        dkeys = { 'default': None, 'keys': [] }
        for dkey in self._object:
            if dkey['default']:
                dkeys['default'] = dkey
            dkeys['keys'].append(dkey)
            
        # Update the deployment keys object
        self._object = dkeys
        
    def _host_get_formula(self):
        """
        Filter host formula responses.
        """
        for formula in self._object:
            try:
                
                # Extract the formula log
                self._unpack_host_formula_log(formula)
                
                # Extract any log history
                for fh in formula['history']:
                    self._unpack_host_formula_log(fh)
                
            # Failed to extract log
            except Exception as e:
                continue
        
    def _host_get(self):
        """
        Filter host responses.
        """
        
        # Single host response
        if isinstance(self._object, dict):
            self._unpack_host(self._object)
            
        # Multiple host response
        if isinstance(self._object, list):
            for host in self._object:
                self._unpack_host(host)
        
    def object(self, object):
        """
        Set the data object to filter.
        """
        
        # Set the internal object container
        self._object = object
        
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