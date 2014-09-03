import re

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common.vars import OS_SUPPORTED
from cloudscape.engine.api.core.ssh import SSHKey
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostDKeys

def get_name_by_uuid(uuid=None):
    """
    Retrieve a host name by UUID.
    """
    if not uuid:
        return None
    return DBHostDetails.objects.filter(uuid=uuid).values()[0]['name']

def get_uuid_by_name(name=None):
    """
    Retrieve a host UUID by name.
    """
    if not name:
        return None
    return DBHostDetails.objects.filter(name=name).values()[0]['uuid']

def get_host_type(uuid=None):
    """
    Get a host OS type by UUID.
    """
    if not uuid:
        return None
    return DBHostDetails.objects.filter(uuid=uuid).values()[0]['os_type']

def is_host_uuid(uuid):
    """
    Check if a UUID belongs to a host.
    """
    if DBHostDetails.objects.filter(uuid=uuid).count():
        return True
    return False

"""
Get Host Deployment Key
"""
def get_dkey(dkey_val=None):
    key_uuid = None
        
    # Deployment key identifier provided
    if dkey_val:
        
        # Look by UUID or name
        by_uuid = DBHostDKeys.objects.filter(uuid=dkey_val).count()
        by_name = DBHostDKeys.objects.filter(name=dkey_val).count()
        if not by_uuid and not by_name:
            return False
        if by_uuid:
            key_uuid = DBHostDKeys.objects.filter(uuid=dkey_val).values()[0]['uuid']
        if by_name:
            key_uuid = DBHostDKeys.objects.filter(name=dkey_val).values()[0]['uuid']
    
    # Look for a default key
    else:
        if not DBHostDKeys.objects.filter(default=True).count():
            return False
        key_uuid = DBHostDKeys.objects.filter(default=True).values()[0]['uuid']
    
    # Decrypt the deployment keypair
    keypair = SSHKey().decrypt(key_uuid, dkey=True)
    return keypair['priv_key']

""" Host Exists

A helper method to check if the host UUID exists in the database.

@type   uuid: The UUID of the host to check for
@param  uuid: string
@return boolean
"""
def host_exists(uuid=None, ip=None):
    if not uuid and not ip:
        return False
    if uuid:
        if not DBHostDetails.objects.filter(uuid=uuid).count():
            return False
        return True
    if ip:
        if not DBHostDetails.objects.filter(ip=ip).count():
            return False
        return True
    return False

"""
Host Support Check

Takes a set of system properties to see if the host type is supported
by CloudScape. If checking for a specific formula, you can override
the supported OS list.
"""
def supported(distro=None, version=None, arch=None, values=False):
    _supported = None
    
    # Architecture alternate formats
    arch_alt = {
        'x86_64': ['AMD64', '64bit'],
        'i386':   ['32bit', 'i686']
    }
    
    # Supports version strings
    if values and isinstance(values, list):
        _supported = values
    else:
        _supported = OS_SUPPORTED
    
    # Set the distro name to lowercase for comparison
    distro = distro.lower()
    
    # Check if the target distribution is supported
    supports = False
    for os in _supported:
        d = re.compile('(^[^\/]*)\/.*$').sub(r'\g<1>', os)
        v = re.compile('^[^\/]*\/([^\/]*)\/.*$').sub(r'\g<1>', os)
        a = re.compile('^.*\/([^\/]*$)').sub(r'\g<1>', os)
            
        # Test if supported
        if d.lower() == distro:
            if v in version:
                if (a in arch) or (arch in arch_alt[a]): 
                    supports = True
    
    # Return the support flag
    return supports