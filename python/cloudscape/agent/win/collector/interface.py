import os
import re
import time
import psutil
import win32pdh
import platform
import netifaces
from datetime import timedelta

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.common.collection import Collection
from cloudscape.agent.config import AgentConfig

# CloudScape Libraries
from cloudscape.agent.win.collector.base import CollectorBase

# Configuration and logger objects
CONFIG = AgentConfig().get()
LOG    = logger.create('cloudscape.agent.win.collector', CONFIG.log.agent)

"""
Windows Collector Interface
"""
class CollectorInterface(CollectorBase):
    
    # Class constructor
    def __init__(self):
        super(CollectorInterface, self).__init__()
        
    """ Define Partition Name """
    def _part_name(self, part):
        if part['properties']['Bootable']:
            return 'BOOT'
        else:
            return '%s:/' % self.partition_get_drives(part['number'])[0]
        
    """ Operating System Information """
    def _sys_get_os(self):
        return {
            'distro':  platform.system(),
            'version': platform.win32_ver()[0],
            'arch':    platform.architecture()[0],
            'kernel':  'N/A',
            'type':    platform.system(),
            'csd':     platform.win32_ver()[1],
        }
        
    """ System: Partitions """
    def _sys_get_partition(self):
        parts = []
        for partition in disk.partitions:
            part_name = self._part_name(partition)
            parts.append({
                'name':       part_name,
                'bootable':   partition['properties']['Bootable'],
                'size':       partition['properties']['Size'],
                'fstype':     'NTFS',
                'mountpoint': part_name
            })
        
    """ System: Disks """
    def _sys_get_disk(self):
        disks = []
        for disk in self.disks:
            disks.append({
                'name': 'PhysicalDrive%s' % disk.number,
                'size': disk.properties['Size']
            })
        return disks
        
    """ System Network Interfaces """
    def _sys_get_net(self):
        netifs = []
        for network in self.networks:
            netifs.append({
                'id':     network.id,
                'hwaddr': network.properties['MACAddress'],
                'ipv4': {
                    'addr':      network.properties['IPAddress'][0],
                    'netmask':   network.properties['IPSubnet'][0],
                    'gateway':   network.properties['DefaultIPGateway'][0],
                    'broadcast': netifaces.ifaddresses(network.id)[2][0]['broadcast']
                }
            })
        return netifs
        
    """ System: Memory Details """
    def _sys_get_mem(self):
        return {
            'total': psutil.phymem_usage().total
        }
    
    """ System: CPU Details """
    def _sys_get_cpu(self):
        cpus = []
        for cpu in self.cpus:
            cpus.append({
                'number': cpu.number,
                'cores':  cpu.properties['NumberOfCores'],
                'model':  cpu.properties['Name']
            })
        return cpus
    
    """ Poller: Get Disk Usage """
    def _poll_get_disk(self):
        _drive_io = psutil.disk_io_counters(perdisk=True)
        drives = {}
        for disk in self.disks:
            for drive in disk.drives:
                _drive_id   = drive['properties']['DeviceID']
                _disk_num   = self.drive_get_disk(drive['letter'])
                _disk_name  = 'PhysicalDrive%s' % _disk_num
                _drive_use  = psutil.disk_usage(_drive_id)
                drives[drive['letter']] = {}
                drive_use = {
                    'total':   _drive_use.total,
                    'used':    _drive_use.used,
                    'free':    _drive_use.free,
                    'percent': _drive_use.percent                    
                }
                drive_io = {
                    'rcount': _drive_io[_disk_name].read_count,
                    'wcount': _drive_io[_disk_name].write_count,
                    'rbytes': _drive_io[_disk_name].read_bytes,
                    'wbytes': _drive_io[_disk_name].write_bytes,
                    'rtime':  _drive_io[_disk_name].read_time,
                    'wtime':  _drive_io[_disk_name].write_time         
                }
                drives[drive['letter']]['use'] = drive_use
                drives[drive['letter']]['io']  = drive_io
        return drives
    
    """ Poller: Network Usage """
    def _poll_get_net(self):
        sys_net = psutil.network_io_counters(pernic=True)
        net_io = {}
        for network in self.networks:
            index = 'Ethernet' if ('Ethernet' in sys_net) else 'Local Area Connection'
            stats = sys_net[index]
            net_io[network.properties['IPAddress'][0]] = {
                'bytes_sent':   stats.bytes_sent,
                'bytes_recv':   stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv
            }
        return net_io
        
    """ Poller: Memory Usage """
    def _poll_get_mem(self):
        _mem = psutil.phymem_usage()
        return {
            'total':     _mem.total,
            'used':      _mem.used,
            'free':      _mem.free,
            'percent':   _mem.percent,
        }
        
    """ Poller: CPU Usage """
    def _poll_get_cpu(self):
        _cpu_time = psutil.cpu_times()
        return {
            'used':   psutil.cpu_percent(),
            'user':   _cpu_time.user,
            'system': _cpu_time.system,
            'idle':   _cpu_time.idle
        }
        
    """ Poller: System Uptime """
    def _poll_get_uptime(self):
        wp = win32pdh.MakeCounterPath((None, 'System', None, None, 0, 'System Up Time'))
        wq = win32pdh.OpenQuery()
        wh = win32pdh.AddCounter(wq, wp)
        win32pdh.CollectQueryData(wq)
        uptime_seconds = win32pdh.GetFormattedCounterValue(wh, win32pdh.PDH_FMT_LONG | win32pdh.PDH_FMT_NOSCALE)[1]
        return str(timedelta(seconds = uptime_seconds))
        
    """ System Details Mapper 
    
    Method to return a dictionary of method objects used when finding and returning
    static system details.
    """
    def _sys_mapper(self):
        return {
            'cpu':        self._sys_get_cpu,
            'memory':     self._sys_get_mem,
            'disk':       self._sys_get_disk,
            'partition': self._sys_get_partition,
            'network':   self._sys_get_net,
            'os':        self._sys_get_os
        }
        
    """ Polling Mapper 
    
    Method to return a dictionary of method objects used when finding and returning
    dynamic system details.
    """
    def _poll_mapper(self):
        return {
            'cpu':        self._poll_get_cpu,
            'memory':     self._poll_get_mem,
            'disk':       self._poll_get_disk,
            'network':    self._poll_get_net,
            'uptime':     self._poll_get_uptime
        }
        
    """ Collect System Details 
    
    Method used to collect static information about the host the first time the agent is run. This
    includes CPU, memory, network, and disk device information. Once the first collection has been
    completed, the '.collect' flag is create in the agent home directory to prevent further runs. You
    can force a re-collection of system data by deleting this flag.
    """
    def sys(self):
        collection = ['cpu', 'memory', 'network', 'disk', 'partition', 'os']
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
        collection = ['uptime', 'cpu', 'memory', 'network', 'disk']
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