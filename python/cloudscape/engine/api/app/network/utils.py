import json
import copy
from uuid import uuid4

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.locations.models import DBDatacenters
from cloudscape.engine.api.app.network.models import DBNetworkRouters, DBNetworkBlocksIPv4, DBNetworkBlocksIPv6

class NetworkBlockUpdate:
    """
    Update an existing network IPv4/IPv6 block definition.
    """
    def __init__(self, parent, proto):
        self.api = parent
        
    def launch(self):
        """
        Worker method for updating an existing network IPv4/IPv6 block object.
        """
        return valid()
      
class NetworkBlockIPv4Update(NetworkBlockUpdate):
    """
    Update an existing IPv4 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv4Update, self).__init__(parent, self.api.get_data('protocol'))
        
class NetworkBlockIPv6Update(NetworkBlockUpdate):
    """
    Update an existing IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Update, self).__init__(parent, self.api.get_data('protocol'))
        
class NetworkBlockDelete:
    """
    Delete an existing network IPv4/IPv6 block definition.
    """
    def __init__(self, parent, proto):
        self.api = parent
        
    def launch(self):
        """
        Worker method for deleting an existing network IPv4/IPv6 block object.
        """
        return valid()
      
class NetworkBlockIPv4Delete(NetworkBlockDelete):
    """
    Delete an existing IPv4 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv4Delete, self).__init__(parent, self.api.get_data('protocol'))
        
class NetworkBlockIPv6Delete(NetworkBlockDelete):
    """
    Delete an existing IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Delete, self).__init__(parent, self.api.get_data('protocol'))
      
class NetworkBlockCreate:
    """
    Create a new network IPv4/IPv6 block definition.
    """
    def __init__(self, parent, proto):
        self.api = parent
        
        # Generate a UUID
        self.uuid = str(uuid4())
        
        # Block protocol / protocol label
        self.proto = self.api.get_data('protocol')
        self.proto_label = 'IPv4' if (self.proto == 'ipv4') else 'IPv6'
        
        # Attribute keys
        self.keys = ['desc', 'datacenter', 'network', 'prefix', 'router', 'meta', 'active', 'locked']
        
        # Get attributes
        self.attrs = {x:self.api.get_data(x) for x in self.keys}
              
    def _create_block(self):
        """
        Create the IP block database entry.
        """
        
        # Get the datacenter and router objects
        datacenter = DBDatacenters.objects.get(uuid=self.attrs['datacenter'])
        # Define the creation parameters
        params = {
            'uuid':       self.uuid,
            'network':    self.attrs['network'],
            'prefix':     self.attrs['prefix'],
            'datacenter': datacenter,
            'desc':       self.attrs['desc'],
            'meta':       '{}' if not self.attrs['meta'] else json.dumps(self.attrs['meta']),
            'active':     True if not self.attrs['active'] else self.attrs['active'],
            'locked':     False if not self.attrs['locked'] else self.attrs['locked']    
        }
        
        # If assigning to a router
        if self.attrs['router']:
            params['router'] = DBNetworkRouters.objects.get(uuid=self.attrs['router'])
        
        # IPv4
        if self.proto == 'ipv4':
            DBNetworkBlocksIPv4(**params).save()
        
        # IPv6
        if self.proto == 'ipv6':
            DBNetworkBlocksIPv6(**params).save()
                
    def launch(self):
        """
        Worker method for creating a new IPv4/IPv6 network block object.
        """
        
        # If the protocol is invalid
        if not self.proto in ['ipv4', 'ipv6']:
            return invalid('Failed to create network block, protocol must be <ipv4> or <ipv6>')
        
        # Build a list of authorized datacenters and routers
        auth_datacenters = self.api.acl.authorized_objects('datacenter')
        auth_routers     = self.api.acl.authorized_objects('net_router')
        
        # If the datacenter doesn't exist or isn't authorized
        if not self.attrs['datacenter'] in auth_datacenters.ids:
            return invalid('Cannot create new %s block in datacenter <%s>, not found or access denied' % (self.proto_label, self.attrs['datacenter']))
        
        # If the router doesn't exist or isn't authorized
        if self.attrs['router']:
            if not self.attrs['router'] in auth_routers.ids:
                return invalid('Cannot create new %s block for router <%s>, not found or access denied' % (self.proto_label, self.attrs['router']))
        
        # Create the network block object
        try:
            self._create_block()
            
        # Critical error when creating network block
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create network %s block: %s' % (self.proto_label, str(e))))
        
        # Return the response
        return valid('Successfully created network %s block' % self.proto_label, {
            'uuid': self.uuid,
            'name': self.attrs['named'],
            'desc': self.attrs['desc'],
            'network': self.attrs['network'],
            'prefix': self.attrs['prefix'],
            'active': self.attrs['active'],
            'locked': self.attrs['locked'],
            'datacenter': {
                'name': datacenter.name,
                'uuid': datacenter.uuid
            },
            'router': {
                'name': router.name,
                'uuid': router.uuid
            }
        })
      
class NetworkBlockIPv4Create(NetworkBlockCreate):
    """
    Create a new IPv4 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv4Create, self).__init__(parent, self.api.get_data('protocol'))
    
class NetworkBlockIPv6Create(NetworkBlockCreate):
    """
    Create a new IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Create, self).__init__(parent, self.api.get_data('protocol'))
      
class NetworkBlockGet:
    """
    Retrieve a listing of network IPv4/IPv6 blocks.
    """
    def __init__(self, parent, proto):
        self.api = parent
        
        # Target block / protocol / protocol label
        self.block = self.api.acl.target_object()
        self.proto = proto
        self.proto_label = 'IPv4' if (self.proto == 'ipv4') else 'IPv6'
        
        # Build a list of authorized IPv4/IPv6 blocks
        self.auth_blocks = {
            'ipv4': self.api.acl.authorized_objects('net_block_ipv4'),
            'ipv6': self.api.acl.authorized_objects('net_block_ipv6')
        }
        
    def launch(self):
        """
        Worker method for retrieving network IPv4/IPv6 block details.
        """
      
        # If looking for a specific block
        if self.block:
            
            # If the block doesn't exist or is not authorized
            if not self.block in self.auth_blocks[self.proto].ids:
                return invalid('Failed to retrieve network %s block <%s>, not found or access denied' % (self.proto_label, self.block))
            
            # Return the block details
            return valid(json.dumps(self.auth_blocks[self.proto].extract(self.block)))
            
        # If retrieving all blocks
        else:
            
            # Get both IPv4 and IPv6 blocks
            return valid(json.dumps(self.auth_blocks[self.proto].details))

class NetworkBlockIPv4Get(NetworkBlockGet):
    """
    Retrive details for an IPv4 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv4Get, self).__init__(parent, self.api.get_data('protocol'))
    
class NetworkBlockIPv6Get(NetworkBlockGet):
    """
    Retrive details for an IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Get, self).__init__(parent, self.api.get_data('protocol'))

class NetworkRouterRemoveInterface:
    """
    Remove an interface from an existing router.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target router
        self.router = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method for removing an interface from a router.
        """
        
        return valid()
      
class NetworkRouterAddInterface:
    """
    Add an interface to an existing router.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target router
        self.router = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method for adding an interface to a router.
        """
        
        return valid()
      
class NetworkRouterUpdate:
    """
    Update an existing network router definition.
    """
    def __init__(self, parent):
        self.api = parent
        
    def launch(self):
        """
        Worker method for updating an existing network router object.
        """
        return valid()
      
class NetworkRouterDelete:
    """
    Delete an existing network router definition.
    """
    def __init__(self, parent):
        self.api = parent
        
    def launch(self):
        """
        Worker method for deleting an existing network router object.
        """
        return valid()
      
class NetworkRouterCreate:
    """
    Create a new network router definition.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Generate a UUID
        self.uuid = str(uuid4())
        
        # Name / description / datacenter
        self.name = self.api.get_data('name')
        self.desc = self.api.get_data('desc')
        self.datacenter = self.api.get_data('datacenter')
        
    def launch(self):
        """
        Worker method for creating a new network router object.
        """
        
        # Build a list of authorized datacenters
        auth_datacenters = self.api.acl.authorized_objects('datacenter')
        
        # If the datacenter doesn't exist or isn't authorized
        if not self.datacenter in auth_datacenters.ids:
            return invalid('Cannot create new router in datacenter <%s>, not found or access denied' % self.datacenter)
        
        # Get the datacenter object
        datacenter = DBDatacenters.objects.get(uuid=self.datacenter)
        
        # Create the router object
        try:
            DBNetworkRouters(
                uuid       = self.uuid,
                name       = self.name,
                desc       = self.desc,
                datacenter = datacenter
            ).save()
            
        # Critical error when creating network router
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create network router: %s' % str(e)))
        
        # Return the response
        return valid('Successfully created network router', {
            'uuid': self.uuid,
            'name': self.name,
            'desc': self.desc,
            'datacenter': {
                'name': datacenter.name,
                'uuid': datacenter.uuid
            }
        })
      
class NetworkRouterGet:
    """
    Retrieve a listing of network routers.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target router
        self.router = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method for retrieving network router details.
        """
        
        # Build a list of authorized routers
        auth_routers = self.api.acl.authorized_objects('net_router')
      
        # If looking for a specific router
        if self.router:
            
            # If the router doesn't exist or is not authorized
            if not self.router in auth_routers.ids:
                return invalid('Failed to retrieve router <%s>, not found or access denied' % self.router)
            
            # Return the router details
            return valid(json.dumps(auth_routers.extract(self.router)))
            
        # If retrieving all routers
        else:
            return valid(json.dumps(auth_routers.details))