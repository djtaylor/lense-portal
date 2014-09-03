import re
import wmi
import ipaddress
import pythoncom

# CloudScape Libraries
from cloudscape.agent.win.collector.device import MemoryDevice, CPUDevice, NetworkDevice, DiskDevice
from cloudscape.agent.win.collector.attrs  import WIN32_MEM_ATTRS, WIN32_CPU_ATTRS, \
                                                  WIN32_OS_ATTRS, WIN32_NETWORK_ATTRS, \
                                                  WIN32_DISK_ATTRS, WIN32_PART_ATTRS, \
                                                  WIN32_DRIVE_ATTRS

"""
Windows Collector Base
"""
class CollectorBase(object):
    
    # Class constructor
    def __init__(self):
        pythoncom.CoInitialize()
        self.wmi = wmi.WMI()

        # Disk / Network / CPU / Memory
        self.disks    = []
        self.networks = []
        self.cpus     = []
        self.memory   = []
    
        # Operating System
        self.os       = {}
    
        # Collect base system information
        self._collect()
    
    """ Collect Base System Information """
    def _collect(self):
        self._disk_get()
        self._net_get()
        self._os_get()
        self._cpu_get()
        self._mem_get()
    
    """ IP Routable Check
    
    Helper method to determine whether an IP address is routable or is only used
    locally.
    """
    def _ip_routable(self, ip):
        _addr = ipaddress.ip_address(unicode(ip))
        if _addr.is_private or _addr.is_global:
            return True
        else:
            return False
    
    """ Get Memory Properties
    
    Extract information about the physical memory modules installed in the system.
    """
    def _mem_get(self):
        for mem_module in self.wmi.Win32_PhysicalMemory():
            dimm_num = re.compile('^DIMM([0-9]*$)').sub(r'\g<1>', mem_module.DeviceLocator)
            mem_obj  = MemoryDevice(dimm_num)
            
            # Extract memory module properties
            mem_obj.add_properties(self._get_win32_properties(mem_module, WIN32_MEM_ATTRS))
            
            # Set the base Win32 object
            mem_obj.set_win32obj(mem_module)
            
            # Add the memory object to the modules list
            self.memory.append(mem_obj)
    
    """ Get CPU Properties
    
    Extract information about each processor installed in the system.
    """
    def _cpu_get(self):
        for cpu in self.wmi.Win32_Processor():
            cpu_num = re.compile('^CPU([0-9]*$)').sub(r'\g<1>', cpu.DeviceID)
            cpu_obj = CPUDevice(cpu_num)
            
            # Extract CPU properties
            cpu_obj.add_properties(self._get_win32_properties(cpu, WIN32_CPU_ATTRS))
            
            # Set the base Win32 object
            cpu_obj.set_win32obj(cpu)
            
            # Add the CPU object the processors list
            self.cpus.append(cpu_obj)
    
    """ Get Operating System Properties 
    
    Extract operating system properties from the system's Win32 class.
    """
    def _os_get(self):
        for os in self.wmi.Win32_OperatingSystem():
            properties = self._get_win32_properties(os, WIN32_OS_ATTRS)
            break
        self.os = properties
    
    """ Get Network Devices
    
    Generate a list of IDs associated with network devices. Only include devices
    with either private or public IPv4 addresses.
    """
    def _net_get(self):
        for network_device in self.wmi.Win32_NetworkAdapterConfiguration():
            if network_device.IPAddress:
                ipv4_addr = network_device.IPAddress[0]
                if self._ip_routable(ipv4_addr):
                    net_obj = NetworkDevice(network_device.SettingID)
                    net_properties = {}
                    for attr in WIN32_NETWORK_ATTRS:
                        net_properties[attr] = getattr(network_device, attr)
                        
                    # Extract network device properties
                    net_obj.add_properties(net_properties)
                    
                    # Set the base Win32 object
                    net_obj.set_win32obj(network_device)
                    
                    # Add the network device to the networks list
                    self.networks.append(net_obj)
    
    """ Get Logical Drive Partition
    
    Find the partition that a logical drive resides on.
    """
    def drive_get_partition(self, letter):
        for disk in self.disks:
            for drive in disk.drives:
                if drive['letter'] == letter:
                    return drive['partition']
        return False
    
    """ Get Logical Drive Disk
    
    Find the physical disk that a logical drive resides on.
    """
    def drive_get_disk(self, letter):
        for disk in self.disks:
            for drive in disk.drives:
                if drive['letter'] == letter:
                    return disk.number
        return False
    
    """ Get Drives on Partition 
    
    Find the logical drives that exist on a single partition.
    """
    def partition_get_drives(self, number):
        drives = []
        for disk in self.disks:
            for drive in disk.drives:
                if drive['partition'] == number:
                    drives.append(drive['letter'])
        return drives
    
    """ Get Logical Disks
    
    Return a list of COM objects containing logical disks contained on a specific
    disk partition.
    """
    def _disk_get_logical(self, partition):
        logical_disks = []
        for logical_disk in partition.associators('Win32_LogicalDiskToPartition'):
            logical_disks.append(logical_disk)
        return logical_disks
    
    """ Get Disk Partitions
    
    Return a list of COM objects containing partitions associated with a physical
    disk device.
    """
    def _disk_get_partitions(self, disk):
        partitions = []
        for partition in disk.associators('Win32_DiskDriveToDiskPartition'):
            partitions.append(partition)
        return partitions
    
    """ Extract Win32 Properties """
    def _get_win32_properties(self, obj, attrs):
        properties = {}
        for attr in attrs:
            if hasattr(obj, attr):
                properties[attr] = getattr(obj, attr)
        return properties
    
    """ Get Disk Devices
    
    Generate a list of physical storage devices attached to the machine. Filter
    out any non-fixed devices, such as CD and USB. Also find any partitions
    associated with the fixed physical disks.
    """
    def _disk_get(self):
        for disk in self.wmi.Win32_DiskDrive():
                
            # Ignore any disks without partitions
            if disk.Partitions <= 0:
                continue
            disk_num = re.compile(r'^.*PHYSICALDRIVE([0-9]*$)').sub(r'\g<1>', disk.DeviceID)
            disk_obj = DiskDevice(disk_num)
            
            # Extract disk attributes
            disk_obj.add_disk_properties(self._get_win32_properties(disk, WIN32_DISK_ATTRS))
            
            # Query each partition
            disk_partitions = self._disk_get_partitions(disk)
            for disk_partition in disk_partitions:
                part_num = re.compile(r'^.*Partition[ ]#([0-9]*$)').sub(r'\g<1>', disk_partition.DeviceID)
                disk_obj.add_partition(part_num, disk_partition.Bootable)
            
                # Extract partition attributes
                disk_obj.add_partition_properties(part_num, self._get_win32_properties(disk_partition, WIN32_PART_ATTRS))
            
                # Get the logical disks on each partition
                logical_disks = self._disk_get_logical(disk_partition)
                if logical_disks:
                    for logical_disk in logical_disks:
                        drive_letter = re.compile(r'(^[A-Z]*):$').sub(r'\g<1>', logical_disk.DeviceID)
                        disk_obj.add_drive(drive_letter, part_num)
                        
                        # Extract drive attributes
                        disk_obj.add_drive_properties(drive_letter, self._get_win32_properties(logical_disk, WIN32_DRIVE_ATTRS))
                        
            # Append the disk object
            self.disks.append(disk_obj)