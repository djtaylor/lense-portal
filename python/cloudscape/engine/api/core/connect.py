# CloudScape Libraries
from cloudscape.engine.api.core.ssh import SSHKey
from cloudscape.engine.api.app.host.models import DBHostDetails

"""
Host Connect Details

Shortcut method to construct host connection details.
"""
class HostConnect:
    def details(self, uuid=None):
        if not uuid:
            return False
    
        # Get the host connection details
        host_details  = DBHostDetails.objects.filter(uuid=uuid).values()[0]
        host_ssh_keys = SSHKey().decrypt(uuid=host_details['uuid'])
        
        # Return the connection details
        return {
            'host':   host_details['ip'],
            'port':   host_details['ssh_port'],
            'user':   host_details['user'],
            'key':    host_ssh_keys['priv_key']
        }