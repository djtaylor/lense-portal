"""
Base Device Class

Base class inherited by device-specific classes. Provides common methods
for setting and retrieving device properties.
"""
class DeviceBase(object):
    
    # Win32 base object
    WIN32_OBJ = None
    
    # Class constructor
    def __init__(self):
        
        # Class properties
        self.id         = None
        self.number     = None
        self.properties = {}
        self.partitions = []
        self.drives     = []
    
    """ Add Device Properties 
    
    Base method to add a construct dictionary of keys and values to the properties
    attribute for the instance of this device object.
    """
    def add_properties(self, properties):
        if not properties or not isinstance(properties, dict):
            return False
        self.properties = properties
        
    """ Add Nested Properties
    
    Add properties to a nested object contained in one of the class attributes. Filter
    by base attribute name, parent key and value.
    """
    def add_nested_properties(self, attr, pkey, pval, properties):
        if not hasattr(self, attr):
            return False
        p = getattr(self, attr)
        for c in p:
            if (pkey in c) and (c[pkey] == pval):
                c['properties'] = properties
                return True
        return False
        
    """ Set Win32 Object 
    
    Store the Win32 object extract by the respective WMI method.
    """
    def set_win32obj(self, obj):
        if not obj:
            return False
        self.WIN32_OBJ = obj
        
    """ Partition Exists 
    
    Used when inherited by a disk device subclass object. Check to see if a specific
    partition number exists in the class attributes.
    """
    def partition_exists(self, number):
        for partition in self.partitions:
            if partition['number'] == number:
                return True
        return False

    """ Drive Exists 
    
    Used when inherited by a disk device subclass object. Check to see if a specific
    logical disk drive exists in the class attributes.
    """
    def drive_exists(self, letter):
        for drive in self.drives:
            if drive['letter'] == letter:
                return True
        return False
        
"""
Memory Device Class

Each instance of this class represents a memory module on a Windows system.
This class contains the DIMM number and properties for the module.
"""
class MemoryDevice(DeviceBase):
    
    # Class constructor
    def __init__(self, number):
        super(MemoryDevice, self).__init__()
        self.number = number

"""
CPU Device Class

Each instance of this class represents a single physical core on a Windows
system. This class contains the CPU number and properties for the processor.
"""
class CPUDevice(DeviceBase):
    
    # Class constructor
    def __init__(self, number):
        super(CPUDevice, self).__init__()
        self.number = number

"""
Network Device Class

Each instance of this class represents either a physical or virtual network
interface on a Windows system. This class contains the Windows specific unique
ID for the interface as well as properties.
"""
class NetworkDevice(DeviceBase):
    
    # Class constructor
    def __init__(self, id):
        super(NetworkDevice, self).__init__()
        self.id = id

"""
Disk Device Class

Each instance of this class represents a single physical disk attached to a
Windows system. This class contains the physical disk number and properties
for the disk, as well as partitions residing on the disk and their properties,
as well as logical drives residing on any partitions.
"""
class DiskDevice(DeviceBase):
    
    # Class constructor
    def __init__(self, number):
        super(DiskDevice, self).__init__()
        self.number = number

    """ Add Disk Properties 
    
    Wrapper method for the parent class to add properties since the disk is
    the root object for this class instance.
    """
    def add_disk_properties(self, properties):
        self.add_properties(properties)

    """ Add Partition """
    def add_partition(self, number, bootable=False):
        if not number:
            return False
        self.partitions.append({'number': number, 'bootable': bootable, 'properties': {}})

    """ Add Partition Properties """
    def add_partition_properties(self, number, properties):
        if not self.partition_exists(number) or not properties or not isinstance(properties, dict):
            return False
        self.add_nested_properties(attr='partitions', pkey='number', pval=number, properties=properties)

    """ Add Logical Drive """
    def add_drive(self, letter, partition):
        if not letter or not self.partition_exists(partition):
            return False
        self.drives.append({'partition': partition, 'letter': letter, 'properties': {}})

    """ Add Logical Drive Properties """
    def add_drive_properties(self, letter, properties):
        if not self.drive_exists(letter):
            return False
        self.add_nested_properties(attr='drives', pkey='letter', pval=letter, properties=properties)