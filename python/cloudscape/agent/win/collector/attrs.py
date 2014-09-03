"""
Win32 Object Attributes
"""

# Win32 memory system object attributes
WIN32_MEM_ATTRS = [
    'BankLabel', 'Capacity', 'Caption', 'CreationClassName', 'DataWidth', 'Description', 'DeviceLocator', 'FormFactor', 
    'HotSwappable', 'InstallDate', 'InterleaveDataDepth', 'InterleavePosition', 'Manufacturer', 'MemoryType', 'Model', 
    'Name', 'OtherIdentifyingInfo', 'PartNumber', 'PositionInRow', 'PoweredOn', 'Removable', 'Replaceable',
    'SerialNumber', 'SKU', 'Speed', 'Status', 'Tag', 'TotalWidth', 'TypeDetail', 'Version'
]

# Win32 CPI system object attributes
WIN32_CPU_ATTRS = [
    'AddressWidth', 'Architecture', 'Availability', 'Caption', 'ConfigManagerErrorCode', 'ConfigManagerUserConfig', 
    'CpuStatus', 'CreationClassName', 'CurrentClockSpeed', 'CurrentVoltage', 'DataWidth', 'Description', 'DeviceID', 
    'ErrorCleared', 'ErrorDescription', 'ExtClock', 'Family', 'InstallDate', 'LastErrorCode', 'Level', 'LoadPercentage', 
    'Manufacturer', 'MaxClockSpeed', 'Name', 'NumberOfCores', 'NumberOfLogicalProcessors', 'OtherFamilyDescription', 
    'PNPDeviceID', 'PowerManagementSupported', 'ProcessorId', 'ProcessorType', 'Revision', 'Role', 'SocketDesignation', 
    'Status', 'StatusInfo', 'Stepping', 'SystemCreationClassName', 'SystemName', 'UniqueId', 'UpgradeMethod', 'Version', 
    'VoltageCaps'
]

# Win32 operating system object attributes
WIN32_OS_ATTRS = [
    'BootDevice', 'BuildNumber', 'BuildType', 'Caption', 'CodeSet', 'CountryCode', 'CreationClassName', 
    'CSCreationClassName', 'CSDVersion', 'CSName', 'CurrentTimeZone', 'Debug', 'Description', 'Distributed', 
    'EncryptionLevel', 'ForegroundApplicationBoost', 'FreePhysicalMemory', 'FreeSpaceInPagingFiles', 
    'FreeVirtualMemory', 'InstallDate', 'LargeSystemCache', 'LastBootUpTime', 'LocalDateTime', 'Locale', 
    'Manufacturer', 'MaxNumberOfProcesses', 'MaxProcessMemorySize', 'Name', 'NumberOfLicensedUsers', 
    'NumberOfProcesses', 'NumberOfUsers', 'OperatingSystemSKU', 'Organization', 'OSArchitecture', 'OSLanguage', 
    'OSProductSuite', 'OSType', 'OtherTypeDescription', 'PlusProductID', 'PlusVersionNumber', 
    'PortableOperatingSystem', 'Primary', 'ProductType', 'RegisteredUser', 'SerialNumber', 'ServicePackMajorVersion', 
    'ServicePackMinorVersion', 'SizeStoredInPagingFiles', 'Status', 'SuiteMask', 'SystemDevice', 'SystemDirectory',
    'SystemDrive', 'TotalSwapSpaceSize', 'TotalVirtualMemorySize', 'TotalVisibleMemorySize', 'Version', 
    'WindowsDirectory'
]

# Win32 network object attributes
WIN32_NETWORK_ATTRS = [
    'ArpAlwaysSourceRoute', 'ArpUseEtherSNAP', 'Caption', 'DatabasePath', 'DeadGWDetectEnabled', 
    'DefaultIPGateway', 'DefaultTOS', 'DefaultTTL', 'Description', 'DHCPEnabled', 'DHCPLeaseExpires', 
    'DHCPLeaseObtained', 'DHCPServer', 'DNSDomain', 'DNSDomainSuffixSearchOrder', 'DNSEnabledForWINSResolution', 
    'DNSHostName', 'DNSServerSearchOrder', 'DomainDNSRegistrationEnabled', 'ForwardBufferMemory', 
    'FullDNSRegistrationEnabled', 'GatewayCostMetric', 'IGMPLevel', 'Index', 'InterfaceIndex', 'IPAddress', 
    'IPConnectionMetric', 'IPEnabled', 'IPFilterSecurityEnabled', 'IPPortSecurityEnabled', 'IPSecPermitIPProtocols', 
    'IPSecPermitTCPPorts', 'IPSecPermitUDPPorts', 'IPSubnet', 'IPUseZeroBroadcast', 'IPXAddress', 'IPXEnabled', 
    'IPXFrameType', 'IPXMediaType', 'IPXNetworkNumber', 'IPXVirtualNetNumber', 'KeepAliveInterval', 
    'KeepAliveTime', 'MACAddress', 'MTU', 'NumForwardPackets', 'PMTUBHDetectEnabled', 'PMTUDiscoveryEnabled', 
    'ServiceName', 'SettingID', 'TcpipNetbiosOptions', 'TcpMaxConnectRetransmissions', 'TcpMaxDataRetransmissions', 
    'TcpNumConnections', 'TcpUseRFC1122UrgentPointer', 'TcpWindowSize', 'WINSEnableLMHostsLookup', 'WINSHostLookupFile', 
    'WINSPrimaryServer', 'WINSScopeID', 'WINSSecondaryServer'
]

# Win32 disk object attributes
WIN32_DISK_ATTRS = [
    'Availability', 'BytesPerSector', 'Capabilities', 'CapabilityDescriptions', 'Caption', 
    'CompressionMethod', 'ConfigManagerErrorCode', 'ConfigManagerUserConfig', 'CreationClassName', 
    'DefaultBlockSize', 'Description', 'DeviceID', 'ErrorCleared', 'ErrorDescription', 'ErrorMethodology', 
    'FirmwareRevision', 'Index', 'InstallDate', 'InterfaceType', 'LastErrorCode', 'Manufacturer', 
    'MaxBlockSize', 'MaxMediaSize', 'MediaLoaded', 'MediaType', 'MinBlockSize', 'Model', 'Name', 
    'NeedsCleaning', 'NumberOfMediaSupported', 'Partitions', 'PNPDeviceID', 'PowerManagementCapabilities', 
    'PowerManagementSupported', 'SCSIBus', 'SCSILogicalUnit', 'SCSIPort', 'SCSITargetId', 'SectorsPerTrack', 
    'SerialNumber', 'Signature', 'Size', 'Status', 'StatusInfo', 'SystemCreationClassName', 'SystemName', 
    'TotalCylinders', 'TotalHeads', 'TotalSectors', 'TotalTracks', 'TracksPerCylinder'
]

# Win32 partition object attributes
WIN32_PART_ATTRS = [
    'Access', 'Availability', 'BlockSize', 'Bootable', 'BootPartition', 'Caption','ConfigManagerErrorCode', 
    'ConfigManagerUserConfig', 'CreationClassName', 'Description', 'DeviceID', 'DiskIndex', 'ErrorCleared', 'ErrorDescription', 
    'ErrorMethodology', 'HiddenSectors', 'Index', 'InstallDate', 'LastErrorCode', 'Name', 'NumberOfBlocks', 'PNPDeviceID',
    'PowerManagementCapabilities', 'PowerManagementSupported', 'PrimaryPartition', 'Purpose', 'RewritePartition', 'Purpose', 
    'RewritePartition', 'Size', 'StartingOffset', 'Status', 'StatusInfo', 'SystemCreationClassName', 'SystemName', 'Type'
]

# Win32 logical drive attributes
WIN32_DRIVE_ATTRS = [
    'Access', 'Availability', 'BlockSize', 'Caption', 'Compressed', 'ConfigManagerErrorCode', 'ConfigManagerUserConfig', 
    'CreationClassName', 'Description', 'DeviceID', 'DeviceType', 'ErrorCleared', 'ErrorDescription', 'ErrorMethodology', 
    'FileSystem', 'FreeSpace', 'InstallDate', 'LastErrorCode', 'MaximumComponentLength', 'MediaType', 'Name', 'NumberOfBlocks', 
    'PNPDeviceID', 'PowerManagementCapabilities', 'PowerManagementSupported', 'ProviderName', 'Purpose', 'QuotasDisabled', 
    'QuotasIncomplete', 'QuotasRebuilding', 'Size', 'Status', 'StatusInfo', 'SupportsDiskQuotas', 'SupportsFileBasedCompression', 
    'SystemCreationClassName', 'SystemName', 'VolumeDirty', 'VolumeName', 'VolumeSerialNumber'          
]