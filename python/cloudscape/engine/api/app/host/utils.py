import re
import os
import json
import time
import copy
import base64
from uuid import uuid4

# Django Libraries
from django.conf import settings
from encrypted_fields import EncryptedTextField

# CloudScape Variables
from cloudscape.common.vars import A_INSTALLING, F_RUNNING, C_USER, F_INSTALL, F_UNINSTALL, F_UPDATE, \
                                   H_LINUX, H_WINDOWS, F_MANAGED, F_UNMANAGED, A_LINUX, A_WINDOWS

# CloudScape Libraries
from cloudscape.engine.api.auth.key import APIKey
from cloudscape.common.remote import RemoteConnect
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.core import host as host_utils
from cloudscape.engine.api.core.ssh import SSHKey
from cloudscape.engine.api.core.connect import HostConnect
from cloudscape.engine.api.util.formula.parse import FormulaParse
from cloudscape.engine.api.app.agent.models import DBHostStats
from cloudscape.engine.api.app.formula.models import DBFormulaDetails
from cloudscape.engine.api.app.group.models import DBGroupDetails
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostSSHAuth, DBHostAPIKeys, \
                                                  DBHostFormulas, DBHostDKeys, DBHostGroups, DBHostGroupMembers, \
                                                  DBHostSystemInfo, DBHostServices, DBHostOwner
        
"""
Host Statistics

API class to return a formatted block of JSON with host statistics from a specific
time range. Averages between time intervals will be calculated here. Mainly for
rendering graphs.
"""
class HostStats:
    def __init__(self, parent):
        self.api = parent
        
        # Statistic Objects
        self.stat_obj   = {'chart':{},'table':{}}
        self.stat_count = 1
        self.stat_last  = {'net_io':{},'disk_io':{},'disk_use':{},'mem_use':{},'cpu_use':{}}
        self.stat_keys  = {
            'net_io':   ['bytes_recv', 'bytes_sent'],
            'disk_io':  ['rbytes', 'wbytes'],
            'mem_use':  ['total', 'used'],
            'cpu_use':  ['total', 'used'],
            'disk_use': ['total', 'used']
        }
        
        # Statistics metadata
        self.stat_meta = {
            'net_io':   {'unit': 'B/s', 'label': 'Network I/O'},
            'disk_io':  {'unit': 'B/s', 'label': 'Disk I/O'},
            'mem_use':  {'unit': 'MB', 'label': 'Memory Usage'},
            'cpu_use':  {'unit': '%', 'label': 'CPU Usage'},
            'disk_use': {'unit': 'GB', 'label': 'Disk Usage'}
        }
        
        # Statistics group container
        self.stat_group = {}
        
        # I/O statistics
        self.stat_io_groups = {
            'net_io':   'network_io',
            'disk_io':  'disk_io'
        }
        
        # Table Groups
        self.stat_tb_groups = {
            'mem_top':  {
                'db_key': 'memory_top',
                'labels': {
                    'pid':  'PID',
                    'name': 'Name',
                    'vms':  'Virtual Memory',
                    'rss':  'Real Memory'
                },
                'key':   'name',
                'order': ['name', 'pid', 'vms', 'rss']
            }
        }
        
        # Single-level resource statistics
        self.stat_sr_groups = {
            'mem_use':  'memory_use',
            'cpu_use':  'cpu_use'
        }
        
        # Multi-level resource statistics
        self.stat_mr_groups = {      
            'disk_use': 'disk_use'            
        }
        
    """ Gather Host Statistics
    
    Gather a block of host statistics based on the host UUID, a start, and an end
    date range. If no end date is supplied, the current datetime will be used.
    
    @type    uuid:   string
    @param   uuid:   The target host UUID to retrieve statistics for
    @type    start:  The date to retrieve statistics for
    @param   start:  datetime
    @type    end:    The end date to retrieve statistics for
    @param   end:    datetime
    @return:         A JSON formatted statistics object
    """
    def launch(self):
        date_fmt = '%Y-%m-%d %H:%M:%S'
        
        # Required keys
        required = ['uuid']
        for key in required:
            if not key in self.api.data:
                return invalid('Missing required key \'%s\' for host statistics request' % key)
        
        # Make sure the host exists
        if not host_utils.host_exists(self.api.data['uuid']):
            return invalid('Requested host \'%s\' not found in the database' % self.api.data['uuid'])
         
        # Make sure the start time is valid
        if not 'start' in self.api.data:
            start = None
        else:
            try:
                time.strptime(self.api.data['start'], date_fmt)
                start = self.api.data['start']
            except Exception as e:
                return invalid('Invalid start date format \'%s\', must be YYYY-MM-DD HH:MM:SS' % self.api.data['start'])
         
        # Make sure an end time is valid and defined
        if not 'end' in self.api.data:
            end = None
        else:
            try:
                time.strptime(self.api.data['end'], date_fmt)
                end = self.api.data['end']
            except Exception:
                return invalid(self.api.log.error('Invalid end date format \'%s\', must be YYYY-MM-DD HH:MM:SS' % self.api.data['end']))
         
        # Get an ordered list of statistics by date
        self.api.log.info('Retrieving host \'%s\' statistics: %s -> %s' % (self.api.data['uuid'], start, end))
        stats_by_date = DBHostStats(uuid=self.api.data['uuid']).get(range={'start': start, 'end': end})
        if not stats_by_date:
            return invalid('Failed to retrieve statistics for host \'%s\'' % self.api.data['uuid']) 
        
        # Begin crunching the averages
        for date, stats in stats_by_date.iteritems():
            date_str = date.strftime(date_fmt)
            
            """ Table Data """
            for group, attrs in self.stat_tb_groups.iteritems():
                stat_obj = json.loads(stats[attrs['db_key']])
                self.stat_obj['table'][group] = {
                    'data':   stat_obj,
                    'labels': attrs['labels'],
                    'key':    attrs['key'],
                    'order':  attrs['order']
                }
            
            """ I/O Statistics 
            
            Resource statistics for objects that need to be calculated between two
            time ranges, such as network and disk I/O.
            """
            for group, db_key in self.stat_io_groups.iteritems():
                stat_obj = json.loads(stats[db_key])
                
                # Initialize the I/O group
                if not group in self.stat_obj['chart']:
                    self.stat_obj['chart'][group]   = {
                        'label':     self.stat_meta[group]['label'], 
                        'unit':      self.stat_meta[group]['unit'],
                        'type':      'io',
                        'data_keys': {'x':'date','y':self.stat_keys[group]},
                        'group':     []
                    }
                    self.stat_group[group] = {}
                    
                # Process each IO device
                for dev, dev_stats in stat_obj.iteritems():
                    if not dev in self.stat_group[group]:
                        self.stat_group[group][dev] = { 'label': dev, 'stats': []}
                    
                    # Ignore the first iteration, need to collect to calculate averages in the next loop
                    if not self.stat_count == 1:
                        stat_row = {'date': date_str, 'data': {}}
                        for stat_key in self.stat_keys[group]:
                            stat_row['data'][stat_key] = (dev_stats[stat_key] - self.stat_last[group][dev][stat_key]) / 10
                        self.stat_group[group][dev]['stats'].append(stat_row)
                    else:
                        self.stat_last[group][dev] = {}
                    
                    # Store the last results
                    for stat_key in self.stat_keys[group]:
                        self.stat_last[group][dev][stat_key] = dev_stats[stat_key]
        
            """ Multi-group Resource Statistics 
            
            Resource group for statistics with multiple objects, mainly disk usage
            statistics for each partition.
            """
            for group, db_key in self.stat_mr_groups.iteritems():
                stat_obj = json.loads(stats[db_key])
                
                # Initialize the resource group
                if not group in self.stat_obj['chart']:
                    self.stat_obj['chart'][group]   = {
                        'label':     self.stat_meta[group]['label'], 
                        'unit':      self.stat_meta[group]['unit'],
                        'type':      'use',
                        'data_keys': {'x':'date','y':self.stat_keys[group]},
                        'group':     []
                    }
                    self.stat_group[group] = {}
                
                # Process each group
                for dev, dev_stats in stat_obj.iteritems():
                    if not dev in self.stat_group[group]:
                        self.stat_group[group][dev] = { 'label': dev, 'stats': []}

                    # Skip the first iteration to coincide with I/O counter stats
                    if not self.stat_count == 1:
                        stat_row = {'date': date_str, 'data': {}}
                        for stat_key in self.stat_keys[group]:
                            stat_row['data'][stat_key] = dev_stats[stat_key]
                        self.stat_group[group][dev]['stats'].append(stat_row)
        
            """ Single-group Resource Statistics 
            
            Resource group for statistics with single objects, such as CPU and memory
            usage.
            """
            for group, db_key in self.stat_sr_groups.iteritems():
                stat_obj = json.loads(stats[db_key])
                if not group in self.stat_group:
                    self.stat_group[group] = {}
                if not group in self.stat_group[group]:
                    self.stat_group[group][group] = { 'label': group, 'stats': []}
                if not group in self.stat_obj['chart']:
                    self.stat_obj['chart'][group] = {
                        'label':     self.stat_meta[group]['label'], 
                        'unit':      self.stat_meta[group]['unit'],
                        'type':      'use',
                        'data_keys': {'x':'date','y':self.stat_keys[group]},
                        'group':     []
                    }
                    self.stat_group[group] = {}
        
                # Skip the first iteration to coincide with I/O counter stats
                if not self.stat_count == 1:
                    stats_row = {}
                    for stat_key in self.stat_keys[group]:
                        stats_row[stat_key] = stat_obj[stat_key]
                    self.stat_group[group][group]['stats'].append({'date': date_str, 'data': stats_row})
        
            # Increment the counter
            self.stat_count += 1
        
        # Append and statistic groups
        for group_name, group_devs in self.stat_group.iteritems():
            for group_dev, group_dev_stats in group_devs.iteritems():
                self.stat_obj['chart'][group_name]['group'].append(group_dev_stats)
        
        # For now log the results and return valid
        return valid(self.stat_obj)
            
"""
Host System Information Manager

API method used to gather system information about the managed host. This is used
when gathering initial data when adding the host, and if host data needs to be
refreshed at any point.
"""
class HostSysInfo:
    def __init__(self, parent):
        self.api = parent

        # Extract method mapper
        self.map = self._mapper()

    # Extract Windows Information
    def _extract_win(self):
        sys_info_rsp  = self.remote.execute(['agent sysinfo'])  
        sys_info_json = json.loads(sys_info_rsp[0]['stdout'][0])
        sys_info_out  = sys_info_json['sys']
    
        # If the request failed
        if sys_info_rsp[0]['exit_code'] != 0:
            return invalid(self.api.log.error('Failed to retrieve Windows system information: %s' % str(sys_info_rsp[0]['stderr'])))
    
        # Calculate total CPUs
        total_cpu = 0
        for cpu in sys_info_out['cpu']:
            total_cpu += int(cpu['cores'])
    
        # Return the host system information
        return { 
            'os': {
                'type':    H_WINDOWS,
                'distro':  sys_info_out['os']['distro'],
                'version': sys_info_out['os']['version'],
                'arch':    sys_info_out['os']['arch'],
                'kernel':  None,
                'release': None,
                'csd':     sys_info_out['os']['csd']
            },
            'cpu': {
                'count':   total_cpu,
                'type':    sys_info_out['cpu'][0]['model'],
            },
            'memory': {
                'total':   sys_info_out['memory']['total']
            }
        }
    
    # Extract Linux Information
    def _extract_linux(self):
        
        # Series of commands to gather basic system information
        sys_info_cmds = { 
            'os':        'python -c "import platform; print platform.system().lower()"',
            'distro':    'python -c "import platform; print platform.linux_distribution()[0].lower()"',
            'version':   'python -c "import platform; print platform.linux_distribution()[1]"',
            'release':   'python -c "import platform; print platform.linux_distribution()[2]"',
            'arch':      'python -c "import platform; print platform.architecture()[0]"',
            'kernel':    'python -c "import platform; print platform.uname()[2]"',
            'cpu_count': 'python -c "import multiprocessing; print multiprocessing.cpu_count()"',
            'cpu_model': 'cat /proc/cpuinfo | grep "model name" | head -1',
            'memory':    'cat /proc/meminfo | grep MemTotal' }
        
        # Extract the command strings
        sys_info_cmd_strings = []
        for key, command in sys_info_cmds.iteritems():
            sys_info_cmd_strings.append(command)
            
        # Run the system information commands
        sys_info_exec_out = self.remote.execute(sys_info_cmd_strings)
        
        # Extract the stdout for each command
        sys_info_out = {}
        for output in sys_info_exec_out:
            for cmd_key, cmd_str in sys_info_cmds.iteritems():
                if cmd_str == output['command']:
                    sys_info_out[cmd_key] = output['stdout'][0].rstrip()
        
        # Clean up the CPU model name
        host_cpu_model_raw = re.compile('^.*:[ ](.*$)').sub(r'\g<1>', sys_info_out['cpu_model'])
        host_cpu_model     = re.sub('\s+', ' ', host_cpu_model_raw)
        
        # Get the total memory in megabytes
        host_memory_raw = re.compile('^.*[ ]([0-9]*)[ ].*$').sub('\g<1>', sys_info_out['memory'])
        host_memory     = int(host_memory_raw) / 1024

        # Return the host system information
        return { 
            'os': {
                'type':    H_LINUX,
                'distro':  sys_info_out['distro'],
                'version': sys_info_out['version'],
                'arch':    sys_info_out['arch'],
                'kernel':  sys_info_out['kernel'],
                'release': sys_info_out['release'],
                'csd':     None
            },
            'cpu': {
                'count':   sys_info_out['cpu_count'],
                'type':    host_cpu_model,
            },
            'memory': {
                'total':   host_memory    
            }
        }

    # System information extraction mapper
    def _mapper(self):
        return {
            H_LINUX:   self._extract_linux,
            H_WINDOWS: self._extract_win
        }

    # Extract host information
    def extract(self, remote, type):
        self.api.log.info('Extracting <%s> system information for host' % type)
        
        # Store the remote connection
        self.remote = remote
        
        # Extract the system information
        try:
            sys_info = self.map[type]()
        except Exception as e:
            return invalid(self.api.log.exception('Failed to retrieve system information: %s' % str(e)))
        
        # Make sure the host is supported
        self.api.log.info('Checking for host support: distro=%s, version=%s, arch=%s' % (sys_info['os']['distro'], sys_info['os']['version'], sys_info['os']['arch']))
        if not host_utils.supported(sys_info['os']['distro'], sys_info['os']['version'], sys_info['os']['arch']):
            return invalid(self.api.log.error('Cannot add host - system type %s %s %s is not supported' % (sys_info['os']['distro'], sys_info['os']['version'], sys_info['os']['arch'])))
        self.api.socket.loading('Discovered host type: %s %s %s...' % (sys_info['os']['distro'], sys_info['os']['version'], sys_info['os']['arch']))
        return valid(sys_info)

class HostServiceGet:
    """
    Retrieve a list of services and service statuses.
    """
    def __init__(self, parent):
        self.api     = parent
        
        # Target host
        self.host    = self.api.acl.target_object()

        # Optional target service
        self.service = None if not ('service' in self.api.data) else self.api.data['service']

    def launch(self):
        """
        Worker method for returning host services and service statuses.
        """
        
        # Get a list of authorized hosts
        auth_hosts = self.api.acl.authorized_objects('host')
        
        # If the host does not exist or is not accessible
        if not self.host in auth_hosts.ids:
            return invalid('Cannot retrieve services for host <%s>, host does not exist or access denied' % self.host)
        
        # Host details / services
        host_details  = auth_hosts.extract(self.host)
        host_services = host_details['sys']['services']
        
        # If a target service is specified
        if self.service:
            
            # Look for the host service
            host_service = None
            for s in host_services:
                if s['name'] == self.service:
                    host_service = s
                    break
                
            # If the service was retrieved
            if host_service:
                return valid(json.dumps(host_service))
            
            # If the service was not found
            return invalid('Could not locate service <%s> on host <%s>' % (self.service, self.host))
            
        # If retrieving all services
        else:
            return valid(json.dumps(host_services))
    
class HostServiceSet:
    """
    Set a host service status state. This can be used to either start or stop a
    host service, as well as change the monitoring state.
    """
    def __init__(self, parent):
        self.api     = parent
        
        # Target host
        self.host    = self.api.acl.target_object()

        # Target service / state / monitor state
        self.service = self.api.data['service']
        self.state   = None
        self.monitor = None
        
    def launch(self):
        """
        Worker method for updating a service's state.
        """
        
        # Get a list of authorized hosts
        auth_hosts = self.api.acl.authorized_objects('host')
        
        # If the target host does not exist or is not accessible
        if not self.host in auth_hosts.ids:
            return invalid('Cannot set service <%s> for host <%s>, host does not exist or access denied' % (self.service, self.host))
            
        # Service filter
        filter = {
            'host_id': self.host,
            'name':    self.service
        }
            
        # If the service was not found
        if not DBHostServices.objects.filter(**filter).count():
            return invalid('Cannot set service <%s> for host <%s>, service not found' % (self.service, self.host))
        
        # Get the current service details
        srv_details = DBHostServices.objects.filter(**filter).values()[0]
        
        # Set the service state / monitor state
        self.state   = srv_details['state_target'] if not ('state' in self.api.data) else self.api.data['state']
        self.monitor = srv_details['monitor'] if not ('monitor' in self.api.data) else self.api.data['monitor']
        
        # Update the system service
        DBHostServices.objects.filter(**filter).update(state_target=self.state, monitor=self.monitor)
        
        # Get the update system service
        srv_updated = DBHostServices.objects.filter(**filter).values()[0]
        
        # Successfully updated host service
        return valid('Successfully set host service state', {
            'host':    self.host,
            'service': {
                'name': self.service,
                'state': {
                    'active': srv_updated['state_active'],
                    'target': srv_updated['state_target']
                },
                'monitor': srv_updated['monitor'],
                'host':    srv_updated['host_id']
            },
            'state':   self.state
        })

class HostGroupCreate:
    """
    Create a custom host group.
    """
    def __init__(self, parent):
        self.api  = parent
        
        # Host group UUID
        self.uuid     = str(uuid4())
        
        # Name / formula / metadata / hosts
        self.name     = self.api.data['name']
        self.formula  = None if not ('formula' in self.api.data) else self.api.data['formula']
        self.metadata = '{}' if not ('metadata' in self.api.data) else self.api.data['metadata']
        self.hosts    = None if not ('hosts' in self.api.data) else self.api.data['hosts']
        
    def launch(self):
        """
        Worker method for creating a new host group.
        """
        
        # Check if the group exists
        if DBHostGroups.objects.filter(name=self.api.data['name']).count():
            return invalid('Failed to create host group <%s>, already exists')
        
        # If specifying metadata
        if self.metadata:
            
            # Make sure the metadata is JSON
            try:
                meta_validate = json.dumps(self.metadata)
            except Exception as e:
                return invalid('Invalid metadata, must be in JSON format: %s' % str(e))
        
        # If specifying a formula
        if self.formula:
            
            # Build a list of authorized formulas
            auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')
            
            # Make sure the formula exists and is accessible
            if not self.formula in auth_formulas.ids:
                return invalid('Cannot use formula <%s> for host group, not found or access denied' % self.formula)
        
        # If specifying a list of hosts
        if self.hosts:
            
            # Build a list of authorized hosts
            auth_hosts = self.api.acl.authorized_objects('host', 'host/get')
        
            # Make sure all hosts exist and are accessible
            for host in self.hosts:
                if not host in auth_hosts.ids:
                    return invalid('Cannot use host <%s> for host group, not found or access denied' % host)
        
        # Create the host group
        host_group = DBHostGroups(
            uuid     = self.uuid, 
            name     = self.name, 
            formula  = self.formula, 
            metadata = self.metadata)
        host_group.save()
        
        # If adding host members
        if self.hosts:
            for host in self.hosts:
                
                # Get the host object
                host_obj = DBHostDetails.objects.get(uuid=host)
                
                # Create the membership entry
                DBHostGroupMembers(host=host_obj, group=host_group).save()
        
        # Host group created
        return valid('Successfully created host group', {
            'name':     self.name,
            'formula':  self.formula,
            'uuid':     self.uuid,
            'metadata': self.metadata
        })

class HostGroupDelete:
    """
    API method used to delete a host group and remove membership links.
    """
    def __init__(self, parent):
        self.api      = parent

        # Target host group
        self.hgroup = self.api.acl.target_object()

    def launch(self):
        
        # Construct a list of authorized host groups
        auth_hgroups = self.api.acl.authorized_objects('hgroup')
        
        # Make sure the host group exists and is accessible
        if not self.hgroup in auth_hgroups.ids:
            return invalid('Cannot delete host group <%s>, not found or access denied' % self.hgroup)
        
        # Delete the host group
        try:
            DBHostGroups.objects.filter(uuid=self.hgroup).delete()
            
            # Return the response
            return valid('Successfully deleted host group', {
                'uuid': self.hgroup                                                 
            })
        
        # Critical error when deleting host group
        except Exception as e:
            return invalid(self.api.log.exception('Failed to delete host group: %s' % str(e)))

class HostGroupUpdate:
    """
    API class used to handle update attributes and membership for a host group.
    """
    def __init__(self, parent):
        self.api     = parent
        
        # Target host group
        self.hgroup  = self.api.acl.target_object()
    
        # Host group details
        self.details = None
    
    def _set_formula(self):
        """
        Set the formula value.
        """
        if (self.api.data['formula'] == 'none') or not (self.api.data['formula']):
            return None
        else:
            return self.api.data['formula']
    
    def _set_metadata(self):
        """
        Set the metadata value.
        """
        
        # Return the metadata
        return self.details['metadata'] if not ('metadata' in self.api.data) else self.api.data['metadata']
    
    def launch(self):
        """
        Worker method for updating host group attributes and membership.
        """
        
        # Construct a list of authorized host groups
        auth_hgroups = self.api.acl.authorized_objects('hgroup')
        
        # Make sure the host group exists and is accessible
        if not self.hgroup in auth_hgroups.ids:
            return invalid('Cannot delete host group <%s>, not found or access denied' % self.hgroup)
        
        # Get the host groups details
        self.details = auth_hgroups.extract(self.hgroup)
        
        # If specifying a formula
        if ('formula' in self.api.data) and (self.api.data['formula'] != 'none' and self.api.data['formula']):
            
            # Construct a list of authorized formulas
            auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')
            
            # Make sure the formula exists and is authorized
            if not self.api.data['formula'] in auth_formulas.ids:
                return invalid('Cannot apply formula <%s> to host group, not found or access denied' % self.api.data['formula'])
        
        # If specifying members
        if 'members' in self.api.data:
            
            # Construct a list of authorized hosts
            auth_hosts = self.api.acl.authorized_objects('host', 'host/get')
            
            # Make sure each host is authorized
            for host in self.api.data['members']:
                if not host in auth_hosts.ids:
                    return invalid('Cannot add host <%s> to host group, not found or access denied' % host)
        
        # If specifying metadata
        if 'metadata' in self.api.data:
            try:
                meta_test = json.loads(self.api.data['metadata'])
            except Exception as e:
                return invalid('Failed to update host group <%s>, metadata must be in a valid JSON format' % self.hgroup)
        
        # Set attributes
        hgroup_name     = self.details['name'] if not ('name' in self.api.data) else self.api.data['name']
        hgroup_formula  = self.details['formula'] if not ('formula' in self.api.data) else self._set_formula()
        hgroup_members  = False if not ('members' in self.api.data) else self.api.data['members']
        hgroup_metadata = self._set_metadata()
        
        # Update the host group
        DBHostGroups.objects.filter(uuid=self.hgroup).update(
            name     = hgroup_name,
            formula  = hgroup_formula,
            metadata = hgroup_metadata
        )
        
        # If updating the members
        if hgroup_members:
            
            # Clear existing membership
            DBHostGroupMembers.objects.filter(group=self.hgroup).delete()
            
            # Get the host group object
            hgroup_obj = DBHostGroups.objects.get(uuid=self.hgroup)
            
            # Update membership tables
            for host in hgroup_members:
                
                # Get the host object
                host_obj = DBHostDetails.objects.get(uuid=host)
                
                # Create the membership row
                DBHostGroupMembers(host=host_obj, group=hgroup_obj).save()
        
        # Return the response
        return valid('Successfully update host group')

class HostGroupGet:
    """
    API method used to retrieve a list of host groups. Can filter by group name,
    group ID, and formula ID if the group was created by running a group formula.
    """
    def __init__(self, parent):
        self.api          = parent
        
        # Target host group
        self.hgroup       = self.api.acl.target_object() 
        
        # Authorized host groups and hosts
        self.auth_hgroups = self.api.acl.authorized_objects('hgroup')
        self.auth_hosts   = self.api.acl.authorized_objects('host', 'host/get')
        
    def _get_members(self, hgroup):
        """
        Extract host group membership.
        """
        
        # Container for member details and IDs
        member_details = []
        member_ids     = []
        
        # Extract member details for the host group
        for member in DBHostGroupMembers.objects.filter(group=hgroup['uuid']).values():
            if member['host_id'] in self.auth_hosts.ids:
                
                # Get full details for the host
                host_details = self.auth_hosts.extract(member['host_id'])
                
                # Append the member UUID
                member_ids.append(host_details['uuid'])
                
                # Append only the required host details
                member_details.append({
                    'uuid':         host_details['uuid'],
                    'name':         host_details['name'],
                    'ip':           host_details['ip'],
                    'os_type':      host_details['os_type'],
                    'distro':       host_details['sys']['os']['distro'],
                    'version':      host_details['sys']['os']['version'],
                    'arch':         host_details['sys']['os']['arch'],
                    'datacenter':   host_details['datacenter'],
                    'agent_status': host_details['agent_status']
                })
                
        # Append the member details and IDs
        hgroup['members'] = {
            'details': member_details,
            'ids':     member_ids
        }
        
        # Return the constructed host group object
        return hgroup
        
    def launch(self):
        """
        Worker method for retrieving host group details.
        """
        
        # If retrieving all host groups
        if not self.hgroup:
            
            # Constructed host groups objects
            hgroup_details = []
            
            # Construct membership for each host group
            for hgroup in self.auth_hgroups.details:
                hgroup_details.append(self._get_members(hgroup))
            
            # Return the response
            return valid(hgroup_details)
        
        # If retrieving a single host group
        else:
        
            # Make sure the host group exists and is accessible
            if not self.hgroup in self.auth_hgroups.ids:
                return invalid('Cannot retrieve host group <%s>, not found or access denied' % self.hgroup)
        
            # Return the host group details
            return valid(self._get_members(self.auth_hgroups.extract(self.hgroup)))
        
"""
Get Host Deployment Keys

API method used to retrieve host deployment keys. If no API data is supplied, all 
keys will be return. Can optionally filter by key name or UUID, and the default
key flag. The private key will be stripped from the response, and the public key
returned in decrypted format.
"""
class HostDKeyGet:
    def __init__(self, parent):
        self.api = parent
    
    # Filter out the private key and decode the public key
    def _filter_keys(self, results):
        results_clean = []
        for result in results:
            
            # Decrypt the keypair
            keypair = SSHKey().decrypt(uuid=result['uuid'], dkey=True)
            
            # Create the filtered results object
            this_result = copy.copy(result)
            del this_result['priv_key']
            this_result['pub_key'] = keypair['pub_key'].replace('\n', '')
            results_clean.append(this_result)
        return results_clean
    
    # Get deployment keys
    def launch(self):
        
        # Get by either name or UUID
        if ('name' in self.api.data) or ('uuid' in self.api.data):
            key_uuid = None
            if not 'uuid' in self.api.data:
                if not DBHostDKeys.objects.filter(name=self.api.data['name']).count():
                    return valid([])
                key_uuid = DBHostDKeys.objects.filter(name=self.api.data['name']).values()[0]['uuid']
            else:
                key_uuid = self.api.data['uuid']
    
            # If filtering by default flag
            if 'default' in self.api.data:
                self.api.log.info('Retrieving host deployment keys where <uuid> = \'%s\' and <default> = \'%s\'' % (key_uuid, repr(self.api.data['default'])))
                results = DBHostDKeys.objects.filter(uuid=key_uuid).filter(default=self.api.data['default']).values()
                return valid(self._filter_keys(results))
                
            # No default filter
            else:
                self.api.log.info('Retrieving host deployment keys where <uuid> = \'%s\'' % key_uuid)
                results = DBHostDKeys.objects.filter(uuid=key_uuid).values()
                return valid(self._filter_keys(results))
    
        # Get all deployment keys
        else:
            
            # If filtering by default flag
            if 'default' in self.api.data:
                self.api.log.info('Retrieving all host deployment keys where <default> = \'%s\'' % repr(self.api.data['default']))
                results = DBHostDKeys.objects.filter(default=self.api.data['default']).values()
                return valid(self._filter_keys(results))
                
            # Get all default and non-default keys
            else:
                self.api.log.info('Retrieving all host deployment keys')
                results = DBHostDKeys.objects.values()
                return valid(self._filter_keys(results))
    
"""
Update Host Deployment Key
    
API method used to update existing deployment keys. This is used to change the deployment
key name, default flag, and/or SSH keypair values.
"""
class HostDKeyUpdate:
    def __init__(self, parent):
        self.api = parent

    # Update deployment key
    def launch(self):
        key_row     = None
        key_name    = None
        key_uuid    = None
        key_default = None
        key_public  = None
        key_private = None

        # Make sure either the UUID or name are set
        if not ('name' in self.api.data) and not ('uuid' in self.api.data):
            return invalid(self.api.log.error('Must supply either the key <name> or <uuid>'))
        
        # If directly supplying the UUID
        if 'uuid' in self.api.data:
            key_uuid = self.api.data['uuid']
            if not DBHostDKeys.objects.filter(uuid=key_uuid).count():
                return invalid(self.api.log.error('No deployment key located using UUID \'%s\'' % key_uuid))
            key_row  = DBHostDKeys.objects.filter(uuid=key_uuid).values()[0]
            
            # Optionally update the keypair name
            key_name = key_row['name'] if not 'name' in self.api.data else self.api.data['name']
        
        # Update by name
        else:    
            key_name = self.api.data['name']
            if not DBHostDKeys.objects.filter(name=self.api.data['name']).count():
                return invalid(self.api.log.error('No deployment key located using name \'%s\'' % self.api.data['name']))
            key_row  = DBHostDKeys.objects.filter(name=key_name).values()[0]
            key_uuid = key_row['uuid']
        self.api.log.info('Updating host deployment key \'%s\'' % (key_uuid))

        # If updating SSH key values
        if ('public_key' in self.api.data) or ('private_key' in self.api.data):
            if not ('public_key' in self.api.data) or not ('private_key' in self.api.data):
                return invalid(self.api.log.error('Must supply both the <public_key> and <private_key> if updating either values'))

            # Make sure both values are base64 encoded
            try:
                key_public  = base64.b64decode(self.api.data['public_key'])
                key_private = base64.b64decode(self.api.data['private_key'])
                self.api.log.info('Updating host deployment key \'%s\' public/private SSH keypair' % (key_uuid))
            except Exception as e:
                em = 'Deployment public and private keys must be base64 encoded: %s' % str(e)
                self.api.log.exception(em)
                return invalid(self.api.log.error(em))
            
        # Set the key default flag
        key_default = key_row['default'] if not 'default' in self.api.data else self.api.data['default']
            
        # Update the key
        try:
            
            # Changing the SSH keypair
            if key_public and key_private:
                DBHostDKeys.objects.filter(uuid=key_uuid).update(
                    name     = key_name,
                    default  = key_default,
                    pub_key  = key_public,
                    priv_key = key_private
                )
                
            # Changing key attributes
            else:
                DBHostDKeys.objects.filter(uuid=key_uuid).update(
                    name        = key_name,
                    default     = key_default
                )
                
        # Failed to update key
        except Exception as e:
            em = 'Failed to update deployment key: %s' % str(e)
            self.api.log.exception(em)
            return invalid(em)
        return valid()

"""
Set Host Deployment Key

API method used to managed the public and private deployment SSH keys for Windows
servers. The public and private keys must be submitted in Base64 format, along with
a unique key name and whether or not this should be the new default key.
"""
class HostDKeySet:
    def __init__(self, parent):
        self.api = parent

    # Set deployment key
    def launch(self):
        required = ['private_key', 'public_key', 'name', 'default']
        
        # Make sure required values are set
        for key in required:
            if not key in self.api.data:
                return invalid(self.api.log.error('Missing required key \'%s\' in request body' % key))
            
        # Make sure both values are base64 encoded
        try:
            public_key  = base64.b64decode(self.api.data['public_key'])
            private_key = base64.b64decode(self.api.data['private_key'])
        except Exception as e:
            em = 'Deployment public and private keys must be base64 encoded: %s' % str(e)
            self.api.log.exception(em)
            return invalid(self.log.error(em))
            
        # Check if the key already exists
        if DBHostDKeys.objects.filter(name=self.api.data['name']).count():
            return invalid(self.api.log.error('Target key name \'%s\' already exists, please use the deployment key update endpoint instead' % self.api.data['name']))
            
        # If no keys exists yet, set the first key to the default
        defkey = True if not DBHostDKeys.objects.count() else self.api.data['default']
            
        # Generate a UUID for the keypair
        key_uuid = uuid4()
            
        # Only allow one default key at a time
        if defkey == True:
            DBHostDKeys.objects.update(default=False)
            
        # Install the new keypair
        self.api.log.info('Creating new deployment keypair \'%s\':\'%s\'' % (self.api.data['name'], key_uuid))
        try:
            dkey = DBHostDKeys(
                uuid     = key_uuid,
                name     = self.api.data['name'],
                default  = defkey,
                pub_key  = public_key,
                priv_key = private_key
            )
            dkey.save()
        except Exception as e:
            em = 'Failed to create deployment keypair: %s' % str(e)
            self.api.log.exception(em)
            return invalid(em)
            
        # Update successfull
        return valid(self.api.log.info('Successfully set deployment keypair \'%s\':\'%s\'' % (self.api.data['name'], key_uuid)))
    
"""
Execute Host Command

API method to managed executing arbitrary commands on the remote host. This
method will automatically decrypt the SSH keys and password, and will run the
commands with sudo if using a non-root administrator account.
"""
class HostExec:
    def __init__(self, parent):
        self.api = parent
    
    # Run a list of commands
    def launch(self, host=None, commands={}):
        if not commands or not isinstance(commands, dict) and not host:
            return False
        else:
            
            # Get the connection parameters
            host_details  = DBHostDetails.objects.filter(name=host).values()[0]
            host_ssh_keys = SSHKey().decrypt(uuid=host_details['uuid'])
            if not host_ssh_keys:
                return False
            else:
                 
                # Open an remote conection to the host
                remote = RemoteConnect(sys_type=H_LINUX, conn=HostConnect.details(host_details['uuid'])).open()
                
                # Extract the command strings
                command_strings = []
                for key, command in commands.iteritems():
                    command_strings.append(command)
                
                # Run the commands
                return remote.execute(command_strings)
    
class HostFormulas:
    """
    API class used to handle the HostFormulas utility. Allows the user to retrieve
    formulas for a specific host or all hosts.
    """
    def __init__(self, parent):
        """
        Initialize the HostFormulas utility
        
        :param parent: The APIBase
        :type parent: APIBase
        """
        self.api = parent
    
        # Target host
        self.host = self.api.acl.target_object()
    
    def _row_extract(self, row):
        """
        Extract formula run details from a host formula row.
        """
        row_obj = {}
        for key, value in row.iteritems():
            if key == 'formula':
                row_obj['name'] = DBFormulaDetails.objects.filter(uuid=value).values()[0]['name']
            if key == 'run_params':
                row_obj['run_params'] = {}
                if row[key]:
                    run_params_decrypted = EncryptedTextField().to_python(value)
                    run_params_obj       = json.loads(run_params_decrypted)
                    for param_set in run_params_obj:
                        if param_set['type'] == 'password':
                            row_obj['run_params'][param_set['name']] = 'hidden'
                        else:
                            row_obj['run_params'][param_set['name']] = param_set['value']
            else:
                row_obj[key] = value
        return row_obj
    
    def _formula_construct(self, formula_row=None):
        """
        Helper method to construct the formula details row.
        
        :param formula_row: The formula row retrieved from the database query
        :type formula_row: dict
        :rtype: dict
        """
        if not formula_row:
            return None
        
        # Get the host UUID
        host_uuid = formula_row['host_id']
        
        # Construct the row object and decrypt runtime parameters
        row_obj = self._row_extract(formula_row)
                
        # Formula run history filter
        filter = {
            'current': False,
            'host':    host_uuid,
            'formula': formula_row['formula']
        }
                
        # Construct the formula run history
        row_obj['history'] = []
        for row in DBHostFormulas.objects.filter(**filter).values():
            row_obj['history'].append(self._row_extract(row))
                
        # Return the constructed row object
        return row_obj
    
    def launch(self):
        """
        Worker method used to construct and return formula details that have
        been applied to the host. If a 'host' parameter is supplied, only return
        formula rows for that host, otherwise return a list of all formulas applied
        to all hosts.
        
        :rtype: valid|invalid
        """
        
        # Construct a list of authorized hosts
        authorized_hosts = self.api.acl.authorized_objects('host')
        
        # Retrieve formulas for all hosts
        if not self.host:
            formula_details = []
            
            # Construct the list of host formula details
            for formula_row in DBHostFormulas.objects.filter(current=True).values():
                
                # Only append authorized hosts
                if formula_row['host_id'] in authorized_hosts.ids:
                    formula_details.append(self._formula_construct(formula_row))
            
            # Return the constructed formula details list
            return valid(formula_details)
        
        # Retrieving formula for a specific host
        else:
            
            # Current host formula filter
            filter = {
                'host':    self.host,
                'current': True
            }
            
            # If the host has no formulas
            if not DBHostFormulas.objects.filter(**filter).count():
                return valid({})
            else:
                
                # Reconstruct the host formulas and decrypt the run parameters
                formula_details = []
                for formula_row in DBHostFormulas.objects.filter(**filter).values():
                    formula_details.append(self._formula_construct(formula_row))
                return valid(formula_details)
    
class HostUpdate:
    """
    API class used to handle updating host attributes.
    """
    def __init__(self, parent):
        self.api  = parent
        
        # Target host
        self.host = self.api.acl.target_object()
        
    def _chown(self):
        """
        Change host ownership.
        """
        
        # Construct a list of authorized groups
        auth_groups = self.api.acl.authorized_objects('group', 'group/get')
        
        # If the group does not exist or is not accessible
        if not self.api.data['owner'] in auth_groups.ids:
            return invalid('Failed to change ownership of host <%s>, group <%s> does not exist or access denied' % (self.host, self.api.data['owner']))
        
        # Get the host / group objects
        host_obj  = DBHostDetails.objects.get(uuid=self.host)
        group_obj = DBGroupDetails.objects.get(uuid=self.api.data['owner'])
        
        # If the host has no owner
        if not DBHostOwner.objects.filter(host=self.host).count():
            DBHostOwner(host=host_obj, owner=group_obj).save()
            
        # If changing the host owner
        else:
            
            # Get the host ownership object, update, and save
            owner_obj = DBHostOwner.objects.get(host=self.host)
            owner_obj.owner = group_obj
            owner_obj.save()
            
        # Successfully updated ownership
        return valid()
        
    def launch(self):
        """
        Worker method for handling host attribute updates.
        """
        
        # Construct a list of all authorized hosts
        auth_hosts = self.api.acl.authorized_objects('host', 'host/get')
        
        # If the host does not exist or is not accessible
        if not self.host in auth_hosts.ids:
            return invalid('Failed to update host <%s>, not found in database or access denied' % self.host)
        
        # If changing the ownership of a host
        if 'owner' in self.api.data:
            chown_status = self._chown()
            if not chown_status['valid']:
                return chown_status
            
        # Update the host cache data
        self.api.cache.save_object('host', self.host)
        
        # Host attributes updated
        return valid('Successfully updated host attributes')
    
class HostGet:
    """
    API class used to handle requests to HostGet. This allows a user to retrieve
    either details for a single host, or all hosts.
    
    :todo: Implement more fine grained filters to allow varying levels of retrieval
    """
    def __init__(self, parent):
        """
        Setup the HostGet utility
        
        :param parent: The APIBase
        :type parent: APIBase
        """
        self.api     = parent
    
        # Target host
        self.host    = self.api.acl.target_object()
    
        # Host filters
        self.filters = {} if not ('filter' in self.api.data) else self.api.data['filter']
    
    def launch(self, data=None):
        """
        Worker method to retrieve host details. If a 'host' parameter is found in the
        request body, return details for that host, otherwise return details for all
        hosts.
        
        :rtype: valid|invalid
        """
        
        # Construct a list of all accessible hosts
        authorized_hosts = self.api.acl.authorized_objects('host', None, self.filters)
        
        # If retrieving all hosts
        if not self.host:
                
            # Return the hosts object
            return valid(json.dumps(authorized_hosts.details))
            
        # Retrieve a single host
        else:
            
            # Extract the host
            host_details = authorized_hosts.extract(self.host)
            
            # If the host doesn't exist
            if not host_details:
                return invalid('Could not locate host <%s> in the database' % self.host)
            
            # Return the constructed host object
            return valid(host_details)
     
class HostRemoveFormula:
    """
    Remove a formula that has been applied to a host. Right now all this class does
    is simply remove the database entries for that host. Software cleanup is left up
    to the administrator until I get the workflow for running the uninstaller done.
    Note that a formula must have an 'uninstall.template' file to be able to run the
    uninstaller one this functionality is in place.
    """
    def __init__(self, parent):
        """
        Set up the HostRemoveFormula utility.
        
        :param parent: The APIBase class
        :type parent: APIBase
        """
        self.api       = parent
        
        # Target host / formula / uninstall
        self.host      = self.api.acl.target_object()
        self.formula   = self.api.data['formula'] 
        self.uninstall = False if not (F_UNINSTALL in self.api.data) else self.api.data[F_UNINSTALL]
        
    def _validate(self):
        """
        Helper method used to validate the request parameters before attempting to
        remove the host formula. Make sure all required parameters are set, make sure
        the host actually exists and that the formula has been applied. If the formula
        is internal, return invalid as this must be remove internally by the API.
        
        Also check for dependencies on the target formula. If any exists, return invalid
        and prompt the user to remove them first.
        
        :rtype: valid|invalid
        """
        
        # Make sure the formula has been applied
        if not DBHostFormulas.objects.filter(host=self.host).filter(formula=self.formula).count():
            return invalid(self.api.log.error('Formula <%s> has not been applied to host <%s>' % (self.formula, self.host)))
        formula_row = DBHostFormulas.objects.filter(host=self.host).filter(formula=self.formula).values()[0]
        
        # Check if the formula is internal
        formula_details = DBFormulaDetails.objects.filter(uuid=self.formula).values()[0]
        if formula_details['internal']:
            return invalid('Cannot manually remove formula, internally managed by the API')
        
        # Check if any other formulas depend on the one being removed
        required_formulas = json.loads(formula_row['requires'])
        for required_formula in required_formulas:
            if required_formula == self.formula:
                return invalid(self.api.log.error('Formula dependencies found. Please remove any formulas that depend on <%s> first.' % self.formula))
        
        # If uninstalling the formula completely
        if self.uninstall:
            pass
        
        # Validation successfull
        return valid()
        
    def _uninstall(self):
        """
        Run the formula uninstallation template.
        """
        return valid()
        
        # Generate the script path and object
        script_path, script_obj = FormulaParse(formula=self.formula).uninstaller()
        if not script_path or not script_obj:
            return invalid(self.api.log.error('Failed to parse formula uninstaller into script'))
        
        # Open a connection to the server
        remote = RemoteConnect(sys_type=H_LINUX, conn=HostConnect().details(uuid=self.host)).open()
        
        # Copy the formula script to the remote server
        remote.send_file(local=script_path, mode=750)
        
        # Run the formula on the remote server
        remote.execute(['{sudo} sh %s &> /dev/null &' % script_path])
        remote.close()
        
    def launch(self):
        """
        Worker method to remove a formula from a host. After validating the request parameters,
        do the work of removing the formula.
        
        :type: valid|invalid
        """
        
        # Construct a list of all accessible hosts
        auth_hosts = self.api.acl.authorized_objects('host', 'host/get')
        
        # Make sure the host exists and is accessible
        if not self.host in auth_hosts.ids:
            return invalid('Host <%s> not found or access denied' % self.host)
        
        try:
            hf_status = self._validate()
            if hf_status['valid'] == False:
                return hf_status
        
        # Critical validation error
        except Exception as e:
            return invalid(self.api.log.exception('Failed to validate formula <%s> removal: %s' % (self.formula, str(e))))
        
        # If running the uninstall template
        if self.uninstall:
            try:
                fr_status = self._uninstall()
                if not fr_status['valid']:
                    return fr_status
                
            # Critical uninstallation error
            except Exception as e:
                return invalid(self.api.log.exception('Failed to run formula <%s> uninstaller: %s' % (self.formula, str(e))))
            
        # Delete the host formula entry
        try:
            DBHostFormulas.objects.filter(host=self.host).filter(formula_id=self.formula).delete()
            
            # Construct the web socket response
            web_data = {
                'uuid':    self.host,
                'formula': self.formula
            }
            return valid('Successfully removed formula <%s> from host <%s>' % (self.formula, self.host), web_data)
        
        # Critical database update error
        except Exception as e:
            return invalid(self.api.log.error('Failed to delete host formula <%s>: %s' % (self.formula, str(e))))
          
class HostDelete:
    """
    API class designed to handle requests to the HostDelete utility. You can
    optionally run the agent uninstaller on the target host, or simply remove
    the host from the database if you want to do software cleanup later.
    """
    def __init__(self, parent):
        """
        Construct the HostDelete utility
        
        :param parent: The APIBase
        :type parent: APIBase
        """
        self.api       = parent
            
        # Target host / uninstall agent
        self.host      = self.api.acl.target_object() 
        self.uninstall = False if not (F_UNINSTALL in self.api.data) else self.api.data[F_UNINSTALL]
            
    def launch(self):
        """
        Worker method that does the work of deleting the host. Makes sure the host
        actually exists in the database. If running the uninstaller, launch the
        FormulaServiceRun utility and wait for a response. Afterwards delete the
        host from the database.
        
        :rtype: valid|invalid
        """
          
        # Make sure the host exists
        if not DBHostDetails.objects.filter(uuid=self.host).count():
            return invalid(self.api.log.error('Target host <%s> does not exist, cannot delete' % self.host))
        self.api.log.info('Preparing to remove host <%s>: uninstall_agent=%s' % (self.host, repr(self.uninstall)))
            
        # Get the host object
        host_obj = DBHostDetails.objects.filter(uuid=self.host).values()[0]
            
        # Set the base host parameters
        host_params = {
            'formula':    A_LINUX if (host_obj['os_type'] == H_LINUX) else A_WINDOWS,
            'host_uuid':  self.host,
            'mode':       F_MANAGED,
            'host_type':  host_obj['os_type']
        } 
            
        # Run the agent uninstall formula on the remote host
        if self.uninstall:
            self.api.socket.loading('Uninstalling CloudScape agent on host...')
            formula_response = self.api.util.FormulaServiceRun.launch(host_params, type=F_UNINSTALL)
            if not formula_response['valid']:
                return formula_response
            
        # Delete the host
        try:
            DBHostDetails.objects.filter(uuid=self.host).delete()
            
            # Delete host statistics
            DBHostStats(self.host).delete()
            
            # Construct the web socket response
            web_data = {
                'uuid': self.host
            }
            return valid('Successfully removed agent and host from database', web_data)
        
        # Critical error when removing database entry
        except Exception as e:
            return invalid(self.api.log.error('Failed to delete host <%s> with error: %s' % (self.host, e)))
      
class HostControlAgent:
    """
    API class utility designed to handle starting and stopping the agent on a managed host.
    """
    def __init__(self, parent):
        self.api    = parent
        
        # Target host / control state / host type
        self.host   = self.api.acl.target_object()
        self.state  = self.api.data['state']
        self.type   = None
        
        # Remote connection
        self.remote = None
        
    def _connect(self):
        """
        Open a remote connection to the host.
        """
        connection = RemoteConnect(sys_type=self.type, conn=HostConnect().details(uuid=self.host)).open()
        
        # Failed to open the connection
        if not connection['valid']:
            return connection
        
        # Set the connection object
        self.remote = connection['content']
        
        # Connection OK
        return valid()
        
    def launch(self):
        """
        Worker method for starting/stopping the agent on a managed host.
        """
        
        # Get a list of authorized hosts
        auth_hosts = self.api.acl.authorized_objects('host', 'host/get')
        
        # If the host is not found or not authorized
        if not self.host in auth_hosts.ids:
            return invalid('Failed to control agent on host <%s>, not found in database or access denied' % self.host)
        
        # Extract the host details
        host_details = auth_hosts.extract(self.host)
        
        # Set the host type
        self.type = host_details['os_type']
        
        # Attempt to open a connection
        conn_status = self._connect()
        if not conn_status['valid']:
            return conn_status
        
        # Run the control command
        output = self.remote.execute(['sudo /usr/bin/cloudscape-agent %s > /dev/null 2>&1 &' % self.state])
        if output[0]['exit_code'] != 0:
            return invalid('Failed to run agent control command: %s' % self.state)
        
        # Control success
        return valid('Successfully sent agent control command: %s' % self.state, {
            'uuid':  self.host,
            'state': self.state
        })
      
class HostUpdateAgent:
    """
    API class utility designed to handle updating the agent on a managed host.
    """  
    def __init__(self, parent):
        self.api     = parent
          
        # Target host / host details / host type
        self.host    = self.api.acl.target_object()
        self.details = None
        self.type    = None
        
    def _set_formula_data(self):
        """
        Set the data that will be used when running the update formula.
        """
        return {
            'uuid':      A_LINUX if (self.type == H_LINUX) else A_WINDOWS,
            'host':      self.host,
            'mode':      F_MANAGED,
            'api_key':   DBHostAPIKeys.objects.filter(host=self.host).values()[0]['api_key']
        }
        
    def launch(self):
        """
        Worker method for updating the managed host agent software.
        """
        
        # Get a list of authorized hosts
        auth_hosts = self.api.acl.authorized_objects('host', 'host/get')
        
        # If the host is not found or not authorized
        if not self.host in auth_hosts.ids:
            return invalid('Failed to update agent on host <%s>, not found in database or access denied' % self.host)
        
        # Extract the host details
        self.details = auth_hosts.extract(self.host)
        
        # Set the host type
        self.type = self.details['os_type']
        
        # Construct the formula data
        f_data = self._set_formula_data()
        
        # Run the update formula
        f_response = self.api.util.FormulaServiceRun.launch(f_data, type=F_UPDATE)
        if not f_response['valid']:
            return f_response
        
        # Host agent successfully updated
        return valid('Successfully launched agent update formula on host <%s>' % self.host)
          
class HostAdd:
    """
    API class utility designed to handle setting up new managed hosts. This class will
    validate request parameters, open a remote connection to the host and extract basic
    host details, run the agent installer formula, then finish setting up any required
    host database entries.
    """
    def __init__(self, parent):
        """
        Initialize the HostAdd utility.
        
        :param parent: The APIBase class
        :type parent: APIBase
        """
        self.api       = parent
              
        # Host UUID / remote connection / type
        self.uuid      = str(uuid4())
        self.remote    = None
        self.h_type    = None
             
        # SSH / API keys
        self.ssh_key   = None
        self.api_key   = None
              
        # Host / host connect / formula data
        self.h_data    = None
        self.h_connect = {}
        self.f_data    = None
              
    def _set_connect(self):
        """
        Set up the host connection details. If connecting to a Windows machine, extract
        the deployment SSH keypair from the database. If connecting to a Linux machine,
        grab the required connection attributes from the request body.
        
        :rtype: valid|invalid
        """
        
        # Linux connection
        if self.h_type == H_LINUX:
            self.h_connect = {
                'host':   self.api.data['ip'],
                'port':   self.api.data['ssh_port'],
                'user':   self.api.data['user'],
                'passwd': self.api.data['password']     
            }
            
        # Windows connection
        if self.h_type == H_WINDOWS:
            
            # Get the deployment key
            dkey_val = None if not 'dkey' in self.api.data else self.api.data['dkey']
            dkey     = host_utils.get_dkey(dkey_val)
            if not dkey:
                return invalid(self.api.log.error('Failed to retrieve host deployment key'))
            
            # Format the connect parameters
            self.h_connect = {
                'host':   self.api.data['ip'],
                'port':   self.api.data['ssh_port'],
                'user':   C_USER,
                'key':    dkey
            }
            
        # Set connection attributes
        return valid()
              
    def _set_host(self):
        """
        Construct host data that will be used to run the agent formula installation
        process, as well as create host database entries.
        """
        
        # Required host parameters
        required = {
            H_WINDOWS: ['ip', 'ssh_port', 'name'],
            H_LINUX:   ['ip', 'user', 'password', 'ssh_port', 'name']
        }
        
        # Validate the host type
        if not self.api.data['type'] in [H_LINUX, H_WINDOWS]:
            return invalid('Invalid host type <%s> - must be <linux> or <windows>' % self.api.data['type'])
        self.h_type = self.api.data['type']
        
        # Make sure all required parameters are set
        for param in required[self.h_type]:
            if not param in self.api.data:
                return invalid('Missing required key <%s> in host creation request' % param)
        
        # Make sure a host with the same IP doesn't exist
        if host_utils.host_exists(ip=self.api.data['ip']):
            return invalid(self.api.log.error('Host with IP <%s> already exists in the database' % (self.api.data['ip'])))
        self.api.socket.loading('Generating SSH and API keys...')
        
        # Generate API/SSH Keys
        self.api_key = APIKey().create()
        self.ssh_key = SSHKey().generate()
        
        # Host Connection
        connect_status = self._set_connect()
        if not connect_status['valid']:
            return connect_status
           
        # Set the formula data
        self.f_data = {
            'uuid':      A_LINUX if (self.h_type == H_LINUX) else A_WINDOWS,
            'host':      self.uuid,
            'mode':      F_UNMANAGED if self.h_type == H_LINUX else F_MANAGED,
            'api_key':   self.api_key,
            'pub_key':   self.ssh_key['public_key'],
            'host_type': self.h_type,
            'connect':   self.h_connect,
            'sys':       None
        }
           
        # Host data constructed
        return valid()
                
    def _set_remote(self):
        """
        Open a remote connection the host using the RemoteConnect class found in the
        cloudscape.common.remote module library. Return invalid if the connection fails
        for any reason.
        
        :param connect: The connection parameters for the host, such as username and password
        :type connect: dict
        :rtype: valid|invalid
        """
        
        # Open an remote conection to the host
        self.api.socket.loading('Connecting to remote host...')
        try:
            remote_rsp = RemoteConnect(sys_type=self.h_type, conn=self.h_connect).open()
            if not remote_rsp['valid']:
                return invalid(self.api.log.error('Failed to establish SSH connection to host <%s>' % self.api.data['ip']))
            self.remote = remote_rsp['content']
        except Exception as e:
            return invalid(self.api.log.exception('An exception occured when connecting to host <%s>: %s' % (self.api.data['ip'], str(e))))
        return valid()
       
    def _set_host_db(self):
        """
        Set up the host database entries after running the agent formula.
        
        1.) Host Details
        2.) Host SSH Auth
        3.) Host API Keys
        
        :rtype: valid|invalid
        """
        self.api.socket.loading('Creating host database entries...')
        
        # Parent host object
        parent_host = None
        
        # Define the host database params
        db_params = {
            'details': {
                'uuid':         self.uuid,
                'name':         self.api.data['name'],
                'ip':           self.api.data['ip'],
                'ssh_port':     self.api.data['ssh_port'],
                'user':         C_USER,
                'os_type':      self.h_type,
                'agent_status': A_INSTALLING
            },
            'sysinfo': {
                'host':         parent_host,
                'network':      '[]',
                'firewall':     '{}',
                'partition':    '[]',
                'memory':       json.dumps(self.f_data['sys']['memory']),
                'disk':         '[]',
                'cpu':          json.dumps(self.f_data['sys']['cpu']),
                'os':           json.dumps(self.f_data['sys']['os']),
                'services':     '[]'
            },
            'sshauth': {
                'id':           None, 
                'host':         parent_host,
                'pub_key':      self.ssh_key['public_key'], 
                'priv_key':     self.ssh_key['private_key']
            },
            'apikey':  {
                'id':           None,
                'host':         parent_host,
                'api_key':      self.api_key
            } 
        }
        
        # Create the host details database entry
        try:
            parent_host = DBHostDetails(**db_params['details'])
            parent_host.save()
            
            # Saving the parent host object
            self.api.log.info('Setting host details for <%s>' % self.uuid)
            
            # Host system information
            DBHostSystemInfo(**db_params['sysinfo']).save()
            self.api.log.info('Setting host system information for <%s>' % self.uuid)
            
            # Host SSH information
            DBHostSSHAuth(**db_params['sshauth']).save()
            self.api.log.info('Setting SSH authentication data for <%s>' % self.uuid)
            
            # Host API keys
            DBHostAPIKeys(**db_params['apikey']).save()
            self.api.log.info('Setting API keys for <%s>' % self.uuid)
            
        # Critical error when saving host database entries
        except Exception as e:
            return invalid(self.api.log.exception('Failed to save new host details to the database: %s' % str(e)))
             
        # Host database set
        return valid(parent_host)
                    
    def launch(self):   
        """
        API class to add a new Linux or Windows managed host to the database and deploy
        agent software. In the case of Linux, the agent software is installed for the 
        first time. In the case of Windows, the installed agent is activated with a new
        configuration file and host attributes, such as UUID and API key.
        
        First validate the host data, the set up a remote connection to the host. Extract
        system information to initialize the database entry. Run the respective agent
        formula on the target host.
        
        If successfull, finish setting up the database entries and return.
        
        :rtype: valid|invalid
        """
        
        # Check new host data
        host_rsp = self._set_host()
        if not host_rsp['valid']:
            return host_rsp
        self.api.log.info('Adding new managed host <%s>: uuid=<%s>' % (self.api.data['ip'], self.uuid))
        
        # Set the remote connection
        remote_rsp = self._set_remote()
        if not remote_rsp['valid']:
            return remote_rsp
        
        # Validate the host and gather system information
        host_rsp = self.api.util.HostSysInfo.extract(self.remote, self.h_type)
        if not host_rsp['valid']:
            return host_rsp
        self.f_data['sys'] = host_rsp['content']
        
        # Run the agent installation formula on the remote host
        self.api.socket.loading('Installing CloudScape agent on new host...')
        formula_response = self.api.util.FormulaServiceRun.launch(self.f_data, type=F_INSTALL)
        if not formula_response['valid']:
            return formula_response
        
        # Create the initial host database entries
        host_db_rsp = self._set_host_db()
        if not host_db_rsp['valid']:
            return host_db_rsp
        host_details = host_db_rsp['content']
            
        # Create the agent formulas entry
        try:
            DBHostFormulas(
                host        = host_details,
                formula     = self.f_data['uuid'],
                exit_status = F_RUNNING,
                exit_code   = 0,
                exit_msg    = 'Formula currently running...',
                requires    = '[]',
                run_params  = '{}'
            ).save()
            self.api.socket.loading('Creating agent formula entry in host formulas table for <%s>' % self.uuid)
            
        # Critical error when saving agent formula entry
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create agent formula entry to the database: %s' % e))
            
        # Construct the web socket response
        web_data = {
            'uuid': self.uuid,
            'name': self.api.data['name'],
            'ip':   self.api.data['ip'],
            'sys':  self.f_data['sys'],
            'type': self.h_type,
        }
            
        # New host created
        return valid('Successfully added host <%s> and installed agent' % self.api.data['name'], web_data)