import os
import re
import json
import psutil
import pyudev
import platform
import netifaces
from subprocess import PIPE, Popen
from datetime import timedelta

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common.utils import find_restop
from cloudscape.agent.common.config import AgentConfig

# Embedded 'python-iptables'
try:
    import cloudscape.common.iptc as iptc
    IPT_ENABLED = True
except:
    IPT_ENABLED = False

# Configuration and logger objects
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.linux.collector', CONFIG.log.agent)

# PyUDEV Properties
PD_PHYSICAL = '8'
PD_DISK     = 'disk'

"""
Agent System Collector

Class used to collect various details about the local system used when updating
system metadata and polling data.
"""
class AgentCollector:

    # Synchronized API data
    sync_data = {}

    def synchronize(self, response):
        """
        Extract the synchronization data response.
        """
        
        # Retrieved data
        if response['code'] == 200:
            self.sync_data = json.loads(response['body'])
            LOG.info('Retrieved synchronization data: HTTP 200')
            
        # Error when retrieving data
        else:
            LOG.info('Data synchronization error: HTTP %s: %s' % (response['code'], response['body']))

    """ Bytes Conversion """
    def _bytesto(self, b, t='G'):
        r = None
        if t == 'T':
            r = (((float(int(b)) / 1024) / 1024) / 1024) / 1024
        if t == 'G':
            r = ((float(int(b)) / 1024) / 1024) / 1024
        if t == 'M':
            r = (float(int(b)) / 1024) / 1024
        return '%.2f' % r

    """ PSUtil Wrapper 
    
    Wrapper method for psutil to use the best available method for retrieving memory
    availability and usage. Also used to avoid and deprecation warnings.
    """
    def _get_memory(self):
        if hasattr(psutil, 'virtual_memory') and callable(psutil.virtual_memory):
            return psutil.virtual_memory()
        else:
            return psutil.phymem_usage()

    """ Collect Disk Size 
    
    Collect the raw size in bytes of a disk device under Linux by using fdisk and
    passing the device name as a parameter.
    """
    def _disk_size(self, dev):
        p   = Popen('fdisk -l %s' % dev, shell=True, stdout=PIPE, stderr=PIPE)
        o,e = p.communicate()
        s   = o.split('\n')
        for l in s:
            if re.match(r'^Disk[ ]?%s.*bytes.*$' % dev, l):
                return re.compile('^.*,[ ]([0-9]*)[ ]bytes$').sub(r'\g<1>', l)
       
    """ NIC Has Address """
    def _nic_has_addr(self, nic):
        try:
            info = netifaces.ifaddresses(nic)
            ipv4 = info[2][0]['addr']
            return True
        except:
            return False
       
    """ Get Network Gateway 
    
    Attempt the get the gateway IP for a specific NIC by parsing the kernel routing
    table. Return nothing if no default gateway found.
    """
    def _net_gateway(self, nic):
        p   = Popen(['netstat -nr'], shell=True, stdout=PIPE, stderr=PIPE)
        o,e = p.communicate()
        s   = o.split('\n')
        c   = 0
        gw  = None
        for l in s:
            if re.match(r'^0\.0\.0\.0.*%s$' % nic, l):
                gw = re.compile(r'^0\.0\.0\.0[ ]*([0-9\.]*)[ ]*.*$').sub(r'\g<1>', l)
        return gw
        
    """ Count Output Lines 
    
    Used mainly for calculating the number of physical CPUs in '/proc/cpuinfo', as well
    as the number of cores per CPU in the same file.
    """
    def _col(self, cmd):
        p   = Popen([cmd], shell=True, stdout=PIPE, stderr=PIPE)
        o,e = p.communicate()
        s   = o.split('\n')
        c   = 0
        for l in s:
            if l.strip():
                c += 1
        return c
        
    def _sys_set_services(self, services):
        """
        If the target state of a service is different from the active state, attempt to 
        start/stop the service.
        """
        
        # Set service state
        def set_state(name, state, controller):
            
            # Service action / service controller
            action  = 'start' if (state) else 'stop'
            control = ['initctl', action, name] if (controller == 'initctl') else ['service', name, action]
            
            # Attempt to run the service action
            p   = Popen(control, stdout=PIPE, stderr=PIPE)
            o,e = p.communicate()
            
            # If the command succeeded
            if p.returncode == 0:
                LOG.info('Successfully changed service <%s> state: %s' % (name, ' '.join(control)))
                return True
                
            # If the command failed
            else:
                LOG.error('Failed to <%s> service <%s>: %s, exit_code=%s, stderr=%s' % (action, name, ' '.join(control), str(p.returncode), str(e)))
                return False
        
        # Process each service
        for s in services:
            if s['state']['active'] != s['state']['target']:
                s_active = 'start' if (s['state']['active'] == True) else 'stop'
                s_target = 'start' if (s['state']['target'] == True) else 'stop'
                
                # Log the service state change
                LOG.info('Changing service <%s> state: <%s> to <%s>' % (s['name'], s_active, s_target))
                
                # If the state change was successful
                if set_state(s['name'], s['state']['target'], s['controller']):
                    s['state']['active'] = s['state']['target']
                    
                # If the state change failed
                else:
                    s['state']['target'] = s['state']['active']
        
    def _sys_get_services(self):
        """
        Return a list of dictionaries, containing an entry for every managed service found
        on the host, and a boolean value for the status.
        """
        srv_list   = []
        srv_status = []
        
        # Get the current distribution
        distro     = platform.linux_distribution()[0].lower()
        
        # Internal command handler
        def check_service(cmds):
            p   = Popen(cmds, stdout=PIPE, stderr=PIPE)
            o,e = p.communicate()
            return (o.split('\n') + e.split('\n'))
        
        # Check services managed with 'initctl'
        def initctl_running(name):
            p   = Popen(['initctl', 'status', name], stdout=PIPE, stderr=PIPE)
            o,e = p.communicate()
            return True if ('running' in o) else False
        
        # Check services managed with 'service'
        def srvc_running(name):
            p   = Popen(['service', name, 'status'], stdout=PIPE, stderr=PIPE)
            o,e = p.communicate()
            return True if (('running' in o) and not ('not' in o)) else False
        
        # Service mapper
        service_map = {
            'service': {
                'regex':  re.compile(r'^.*\]\s+(.*$)'),
                'status': srvc_running
            },
            'initctl': {
                'regex':  re.compile(r'(^[^ ]*).*$'),
                'status': initctl_running
            }
        }
        
        # Get target service state
        def target_state(name, type):
            if 'services' in self.sync_data:
                for s in self.sync_data['services']:
                    if s['name'] == name:
                        return s['state']['target']
            return service_map[type]['status'](name)
        
        # Set the service status
        def set_status(service, type):
            name = service_map[type]['regex'].sub(r'\g<1>', service)
            if name.strip() and not name in srv_list:
                srv_list.append(name)
                srv_status.append({
                    'name':    name,
                    'controller': type,
                    'state': {
                        'active': service_map[type]['status'](name),
                        'target': target_state(name, type)
                    }
                })
        
        # If running on an Ubuntu system, prioritize initctl services
        if distro == 'ubuntu':
            for s in check_service(['initctl', 'list']):
                set_status(s, 'initctl')
                    
        # All other system types
        for s in check_service(['service', '--status-all']):
            set_status(s, 'service')
        
        # Look for any changes in service state
        self._sys_set_services(srv_status)
        
        # Return the service details
        return srv_status
        
    """ Operating System Information 
    
    Return a formatted object of operating system information. The data structure
    is the same between Linux and Windows.
    """
    def _sys_get_os(self):
        _distro = platform.linux_distribution()
        return {
            'distro':  _distro[0],
            'version': _distro[1],
            'arch':    platform.architecture()[0],
            'kernel':  platform.release(),
            'type':    platform.system(),
            'csd':     'N/A',
            'release': _distro[2]
        }
    
    """ System: Firewall 
    
    Currently only have support for retrieving IPTables configuration.
    """
    def _sys_get_firewall(self):
        fw_config  = {'type': 'iptables', 'config': {}}
        ipt_config = {}
        
        # If 'python-iptables' fails, assume iptables not being used
        try:
            ipt_table  = iptc.Table(iptc.Table.FILTER)
        except:
            return {}
        
        # Default sytem tables and base rule attributes
        def_tables = ['INPUT', 'OUTPUT', 'FORWARD']
        rule_attrs = ['protocol', 'src', 'dst', 'in_interface', 'out_interface']
        
        # Load the firewall config
        t_count = 0
        for chain in ipt_table.chains:
            tc = str(t_count)
            
            # Initialize the table properties
            ipt_config[tc] = {'chain': chain.name, 'rules': {}}
            
            # Set the default policy if one exists
            if chain.name in def_tables:
                ipt_config[tc]['policy'] = chain.get_policy().name
                
            # Get each rule in the chain
            r_config = {}
            r_count  = 0
            for rule in chain.rules:
                rc           = str(r_count)
                r_config[rc] = {}
                for ra in rule_attrs:
                    if hasattr(rule, ra) and getattr(rule, ra):
                        r_config[rc][ra] = getattr(rule, ra)
                    if hasattr(rule, 'target'):
                        r_config[rc]['target'] = rule.target.name
    
                # Process rule matches
                for match in rule.matches:
                    for p,v in match.parameters.iteritems():
                        r_config[rc][p] = v
                r_count += 1
            ipt_config[tc]['rules'] = r_config
            t_count += 1
        fw_config['config'] = ipt_config
        
        # Return the firewall config
        return fw_config
    
    """ System: Partitions 
    
    Return a formatted object of system partitions. The data structure is the same
    between Linux and Windows. The return value is a list which contains one dictionary
    object for every partition device found.
    """
    def _sys_get_partition(self):
        parts = psutil.disk_partitions()
        partitions = []
        for part in parts:
            partitions.append({
                'name':       part.device,
                'bootable':   True if (part.mountpoint == '/boot') else False,
                'size':       self._disk_size(part.device),
                'fstype':     part.fstype,
                'mountpoint': part.mountpoint
            })
        return partitions
        
    """ System: Disks 
    
    Return a formatted object of available physical disks. The data structure is the
    same between Linux and Windows. The return value is a list which contains one dictionary
    object for every physical disk found.
    """
    def _sys_get_disk(self):
        context = pyudev.Context()
        disks = []
        for disk in context.list_devices(DEVTYPE=PD_DISK):
            MAJOR = disk.attributes['dev'].split(':')[0]
            if (MAJOR == PD_PHYSICAL):
                disks.append({
                    'name': disk.device_node,
                    'size': self._disk_size(disk.device_node)
                })
        return disks
        
    """ System Network Interfaces 
    
    Return a formatted object of network interfaces. Ignore interfaces such as loopback,
    localhost, VPN connections, etc. Data structure is the same between Linux and Windows.
    Return a list with one dictionary object for each network interface found.
    """
    def _sys_get_net(self):
        if_list = netifaces.interfaces()
        if 'lo' in if_list: if_list.remove('lo')
        netifs  = []
        for iface in if_list:
            info  = netifaces.ifaddresses(iface)
            
            # Aliased interface
            if ':' in iface:
                parent = re.compile(r'(^[^:]*):.*$').sub(r'\g<1>', iface)
                pinfo  = netifaces.ifaddresses(parent)
                hwaddr = pinfo[17][0]['addr']
                
            # Physical interface
            else:
                hwaddr = info[17][0]['addr']
                
            # Base attributes
            _base = {
                'id':     iface,
                'hwaddr': hwaddr,   
            }
            try:
                _base['ipv4'] = {
                    'addr':      info[2][0]['addr'],
                    'netmask':   info[2][0]['netmask'],
                    'gateway':   self._net_gateway(iface),
                    'broadcast': info[2][0]['broadcast'],
                }
            except:
                pass
            netifs.append(_base)
        return netifs
    
    """ System: Memory Details 
    
    Simple helper method the return the total available memory in bytes on the system. The
    data structure is the same between Linux and Windows.
    """
    def _sys_get_mem(self):
        return {
            'total': self._bytesto(self._get_memory().total, t='M')
        }
    
    """ System: CPU Details 
    
    Return a formatted object with the details on the system's CPU resources. Data structure
    is the same between Linux and Windows. Each physical CPU is a dictionary in the main list
    object, and each physical CPU entry contains an ID number, core count, and model string.
    """
    def _sys_get_cpu(self):
        
        # Find the CPU model
        p   = Popen('cat /proc/cpuinfo | grep "model name" | head -1', shell=True, stdout=PIPE, stderr=PIPE)
        o,e = p.communicate()
        r   = re.compile('^.*:[ ](.*$)').sub(r'\g<1>', o)
        m   = re.sub('\s+', ' ', r)
        
        # Find the number of physical CPUs
        pcpu_counter = self._col('cat /proc/cpuinfo | grep "physical id" | uniq')
        pcpu_count   = 1 if (pcpu_counter == 0) else pcpu_counter
        pcpu_filter  = False if (pcpu_counter == 0) else True
        
        # Build an array of physical/virtual CPUs
        cpus  = []
        count = 0
        while count < pcpu_count:
            pcpu_cmd   = 'cat /proc/cpuinfo | grep -e "physical\sid\s*:\s%s"' % count if pcpu_filter else 'cat /proc/cpuinfo | grep "processor" | uniq'
            pcpu_cores = self._col(pcpu_cmd)
            if int(pcpu_cores) > 0:
                cpus.append({
                    'number': count,
                    'cores':  pcpu_cores,
                    'model':  m
                })
            count += 1
        return cpus
        
    """ Poller: System Uptime """
    def _poll_get_uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string  = str(timedelta(seconds = uptime_seconds))
        return uptime_string
        
    """ Poller: Disk I/O """
    def _poll_get_disk_io(self):
        sys_part = psutil.disk_partitions()
        sys_dio  = psutil.disk_io_counters(perdisk=True)
        disk_io  = {}
        for part in sys_part:
            pname = re.compile('^.*\/([^\/]*$)').sub(r'\g<1>', part.device)
            rname = part.device if not (os.path.islink(part.device)) else os.path.realpath(part.device)
            iname = re.compile(r'^.*\/([^\/]*$)').sub(r'\g<1>', rname)
            
            # Get the disk IO stats
            disk_io[pname] = {
                'rcount': sys_dio[iname].read_count,
                'wcount': sys_dio[iname].write_count,
                'rbytes': sys_dio[iname].read_bytes,
                'wbytes': sys_dio[iname].write_bytes,
                'rtime':  sys_dio[iname].read_time,
                'wtime':  sys_dio[iname].write_time                 
            }
            
        # Return the disk I/O information
        return disk_io
        
    """ Poller: Disk Usage """
    def _poll_get_disk_use(self):
        disk_use = {}
        for part in psutil.disk_partitions():
            mpoint = part.mountpoint
            sname  = re.compile(r'^.*\/([^\/]*$)').sub(r'\g<1>', part.device)
            pdu    = psutil.disk_usage(mpoint)
            
            # Get the partition usage stats
            disk_use[sname] = {
                'used':       self._bytesto(pdu.used, t='G'),
                'total':      self._bytesto(pdu.total, t='G'),
                'free':       self._bytesto(pdu.free, t='G'),
                'percent':    '%.2f' % pdu.percent               
            }
        return disk_use
        
    """ Poller: Network I/O """
    def _poll_get_net_io(self):
        sys_net  = psutil.network_io_counters(pernic=True)
        net_dict = {}
        for nic, stats in sys_net.iteritems():
            if (nic != 'lo') and (self._nic_has_addr(nic)):
                net_dict[nic] = {
                    'bytes_sent':   stats.bytes_sent,
                    'bytes_recv':   stats.bytes_recv,
                    'packets_sent': stats.packets_sent,
                    'packets_recv': stats.packets_recv
                }
        return net_dict
        
    """ Poller: Memory Top Processes """
    def _poll_get_mem_top(self):
        return find_restop(type='memory')
        
    """ Poller: Memory Usage """
    def _poll_get_mem_use(self):
        _mem = self._get_memory()
        return {
            'total':     self._bytesto(_mem.total, t='M'),
            'used':      self._bytesto(_mem.used, t='M'),
            'free':      self._bytesto(_mem.free, t='M'),
            'percent':   '%.2f' % _mem.percent,
        }
        
    """ Poller: CPU Usage """
    def _poll_get_cpu_use(self):
        _cpu_time = psutil.cpu_times()
        return {
            'used':      psutil.cpu_percent(interval=0.5),
            'total':     100,
            't_user':    _cpu_time.user,
            't_system':  _cpu_time.system,
            't_idle':    _cpu_time.idle,
            't_nice':    _cpu_time.nice,
            't_iowait':  _cpu_time.iowait,
            't_irq':     _cpu_time.irq,
            't_softirq': _cpu_time.softirq
        }
      
    """ System Details Mapper 
    
    Method to return a dictionary of method objects used when finding and returning
    static system details.
    """
    def _sys_mapper(self):
        return {
            'cpu':       self._sys_get_cpu,
            'memory':    self._sys_get_mem,
            'disk':      self._sys_get_disk,
            'partition': self._sys_get_partition,
            'network':   self._sys_get_net,
            'os':        self._sys_get_os,
            'firewall':  self._sys_get_firewall,
            'services':  self._sys_get_services
        }
        
    """ Polling Mapper 
    
    Method to return a dictionary of method objects used when finding and returning
    dynamic system details.
    """
    def _poll_mapper(self):
        return {
            'cpu_use':    self._poll_get_cpu_use,
            'memory_use': self._poll_get_mem_use,
            'memory_top': self._poll_get_mem_top,
            'disk_use':   self._poll_get_disk_use,
            'disk_io':    self._poll_get_disk_io,
            'network_io': self._poll_get_net_io,
            'uptime':     self._poll_get_uptime
        }
        
    """ Collect System Details 
    
    Method used to collect static information about the host the first time the agent is run. This
    includes CPU, memory, network, and disk device information. Once the first collection has been
    completed, the '.collect' flag is create in the agent home directory to prevent further runs. You
    can force a re-collection of system data by deleting this flag.
    """
    def sys(self):
        collection = ['cpu', 'memory', 'network', 'disk', 'partition', 'os', 'firewall', 'services']
        LOG.info('Running system detail groups: %s' % str(collection))
        
        # Construct the system mapper
        sys_map = self._sys_mapper()
        
        # Construct the system data
        sys_info = {}
        for collector in collection:
            sys_info[collector] = sys_map[collector]()
        
        # Return the system data
        return {
            'uuid': CONFIG.agent.uuid,
            'sys':  sys_info
        }
        
    """ Collect Polling Data 
    
    Method used to collect periodic polling data for the local machine. This includes the monitoring
    of CPU usage, memory usage, free disk space, network I/O, disk I/O, and total uptime. Data is 
    stored in the 'cloudscape_host_stats'.'<HOST_UUID>' table for each host.
    """
    def poll(self):
        collection = ['uptime', 'cpu_use', 'memory_use', 'memory_top', 'network_io', 'disk_use', 'disk_io']
        LOG.info('Running system poller groups: %s' % str(collection))
        
        # Construct the poll mapper
        poll_map = self._poll_mapper()
        
        # Construct the polling data
        poll_info = {}
        for collector in collection:
            poll_info[collector] = poll_map[collector]()
        
        # Return the polling data
        return {
            'uuid': CONFIG.agent.uuid,
            'poll': poll_info
        }