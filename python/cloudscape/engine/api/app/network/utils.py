import json
import copy
from uuid import uuid4

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.locations.models import DBDatacenters
from cloudscape.engine.api.app.network.models import DBNetworkRouters, DBNetworkBlocksIPv4, DBNetworkBlocksIPv6, \
                                                     DBNetworkRouterInterfaces

class NetworkBlockUpdate(object):
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
        super(NetworkBlockIPv4Update, self).__init__(parent, 'ipv4')
        
class NetworkBlockIPv6Update(NetworkBlockUpdate):
    """
    Update an existing IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Update, self).__init__(parent, 'ipv6')
        
class NetworkBlockDelete(object):
    """
    Delete an existing network IPv4/IPv6 block definition.
    """
    def __init__(self, parent, proto):
        self.api = parent
        
        # Target protocol / label
        self.proto = proto
        self.proto_label = 'IPv4' if (self.proto == 'ipv4') else 'IPv6'
        
        # Target IP block
        self.block = self.api.acl.target_object()
        
    def _delete_block(self):
        """
        Delete the target IPv4/IPv6 block.
        """
        
        # IPv4
        if self.proto == 'ipv4':
            DBNetworkBlocksIPv4.objects.get(uuid=self.block).delete()
            
        # IPv6
        if self.proto == 'ipv6':
            DBNetworkBlocksIPv6.objects.get(uuid=self.block).delete()
        
    def launch(self):
        """
        Worker method for deleting an existing network IPv4/IPv6 block object.
        """
        
        # Construct a list of authorized network blocks
        auth_blocks = self.api.acl.authorized_objects('net_block_%s' % self.proto)
        
        # If the target IP block isn't found or access is denied
        if not self.block in auth_blocks.ids:
            return invalid('Failed to delete %s block [%s], not found or access denied' % (self.proto_label, self.block))
        
        # Delete the block
        try:
            self._delete_block()
            
        # Error when deleting block
        except Exception as e:
            return invalid('Failed to delete %s block [%s]: %s ' % (self.proto_label, self.block, str(e)))
        
        # Successfully deleted block
        return valid('Successfully deleted %s block' % self.proto_label, {
            'uuid': self.block
        })
      
class NetworkBlockIPv4Delete(NetworkBlockDelete):
    """
    Delete an existing IPv4 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv4Delete, self).__init__(parent, 'ipv4')
        
class NetworkBlockIPv6Delete(NetworkBlockDelete):
    """
    Delete an existing IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Delete, self).__init__(parent, 'ipv6')
      
class NetworkBlockCreate(object):
    """
    Create a new network IPv4/IPv6 block definition.
    """
    def __init__(self, parent, proto):
        self.api = parent
        
        # Generate a UUID
        self.uuid = str(uuid4())
        
        # Block protocol / protocol label
        self.proto = proto
        self.proto_label = 'IPv4' if (self.proto == 'ipv4') else 'IPv6'
              
        # Datacenter / router
        self.datacenter = self.api.get_data('datacenter')
        self.router = self.api.get_data('router')
              
    def _create_block(self):
        """
        Create the IP block database entry.
        """
        
        # Define the creation parameters
        params = {
            'uuid':       self.uuid,
            'network':    self.api.get_data('network'),
            'prefix':     self.api.get_data('prefix'),
            'desc':       self.api.get_data('desc'),
            'meta':       self.api.get_data('meta', None),
            'active':     self.api.get_data('active', True),
            'locked':     self.api.get_data('locked', False)
        }
        
        # If assigning to a datacenter
        if self.datacenter:
            
            # Construct a list of authorized datacenters
            auth_datacenters = self.api.acl.authorized_objects('datacenter')
            
            # If the datacenter is not found or access is denied
            if not self.datacenter in auth_datacenters.ids:
                raise Exception('Could not locate datacenter [%s], not found or access denied' % self.datacenter)
            
            # Set the datacenter object
            params['datacenter'] = DBDatacenters.objects.get(uuid=self.datacenter)
        
        # If assigning to a router
        if self.router:
            
            # Construct a list of authorized routers
            auth_routers = self.api.acl.authorized_objects('net_router')
            
            # If the router is not found or access is denied
            if not self.router in auth_routers.ids:
                raise Exception('Could not locate router [%s], not found or access denied' % self.router)
            
            # Set the router object
            params['router'] = DBNetworkRouters.objects.get(uuid=self.router)
        
        # IPv4
        if self.proto == 'ipv4':
            DBNetworkBlocksIPv4(**params).save()
        
        # IPv6
        if self.proto == 'ipv6':
            DBNetworkBlocksIPv6(**params).save()
                
        # Return the parameters
        return params
                
    def launch(self):
        """
        Worker method for creating a new IPv4/IPv6 network block object.
        """
        
        # If the protocol is invalid
        if not self.proto in ['ipv4', 'ipv6']:
            return invalid('Failed to create network block, protocol must be [ipv4] or [ipv6]')
        
        # Create the network block object
        try:
            params = self._create_block()
            
        # Critical error when creating network block
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create network %s block: %s' % (self.proto_label, str(e))))
        
        # Construct the web data
        web_data = {
            'uuid': self.uuid,
            'desc': params['desc'],
            'network': params['network'],
            'prefix': params['prefix'],
            'active': params['active'],
            'locked': params['locked']
        }
        
        # If attaching to a datacenter
        if 'datacenter' in params:
            web_data.update({'datacenter': {
                'name': params['datacenter'].name,
                'uuid': params['datacenter'].uuid
            }})
            
        # If attaching to a router
        if 'router' in params:
            web_data.update({'router': {
                'name': params['router'].name,
                'uuid': params['router'].uuid
            }})
        
        # Return the response
        return valid('Successfully created network %s block' % self.proto_label, web_data)
      
class NetworkBlockIPv4Create(NetworkBlockCreate):
    """
    Create a new IPv4 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv4Create, self).__init__(parent, 'ipv4')
    
class NetworkBlockIPv6Create(NetworkBlockCreate):
    """
    Create a new IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Create, self).__init__(parent, 'ipv6')
      
class NetworkBlockGet(object):
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
                return invalid('Failed to retrieve network %s block [%s], not found or access denied' % (self.proto_label, self.block))
            
            # Return the block details
            return valid(json.dumps(self.auth_blocks[self.proto].extract(self.block)))
            
        # If retrieving all blocks
        else:
            
            # Return the IP protocol block
            return valid(json.dumps(sorted(self.auth_blocks[self.proto].details, key=lambda k: k['network'])))

class NetworkBlockIPv4Get(NetworkBlockGet):
    """
    Retrive details for an IPv4 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv4Get, self).__init__(parent, 'ipv4')
    
class NetworkBlockIPv6Get(NetworkBlockGet):
    """
    Retrive details for an IPv6 network block.
    """
    def __init__(self, parent):
        super(NetworkBlockIPv6Get, self).__init__(parent, 'ipv6')

class NetworkRouterRemoveInterface:
    """
    Remove an interface from an existing router.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target router / interface
        self.router = self.api.acl.target_object()
        self.interface = self.api.get_data('interface')
        
    def launch(self):
        """
        Worker method for removing an interface from a router.
        """
        
        # Get a list of authorized routers
        auth_routers = self.api.acl.authorized_objects('net_router')
        
        # If the router doesn't exist or access denied
        if not self.router in auth_routers.ids:
            return invalid('Cannot remove interface, router not found or access denied' % self.router)
        
        # Extract the router details
        router_details = auth_routers.extract(self.router)
        
        # Make sure the interface exists on the router
        interface_found = False
        for interface in router_details['interfaces']:
            if interface['uuid'] == self.interface:
                interface_found = True
        
        # If the interface is not attached to the router
        if not interface_found:
            return invalid('Cannot remove interface [%s] from router [%s], interface not found' % (self.interface, self.router))
        
        # Delete the interface
        DBNetworkRouterInterfaces.objects.get(uuid=self.interface).delete()
        
        # Deleted the interface
        return valid('Successfully removed router interface', {
            'uuid': self.interface
        })
      
class NetworkRouterUpdateInterface:
    """
    Update an existing router interface.
    """
    def __init__(self, parent):
        self.api = parent
      
        # Target router / interface
        self.router = self.api.acl.target_object()
        self.interface = self.api.get_data('interface')
      
    def _update_interface(self):
        """
        Update the interface attributes.
        """
      
        # Get the interface object
        interface_obj = DBNetworkRouterInterfaces.objects.get(uuid=self.interface)
      
        # Name / description / hardware address
        if 'name' in self.api.data:
            interface_obj.name = self.api.data['name']
        if 'desc' in self.api.data:
            interface_obj.desc = self.api.data['desc']
        if 'hwaddr' in self.api.data:
            interface_obj.hwaddr = self.api.data['hwaddr']
        
        # IPv4 address / network
        if 'ipv4_addr' in self.api.data:
            interface_obj.ipv4_addr = None if not self.api.data['ipv4_addr'] else self.api.data['ipv4_addr']
        if 'ipv4_net' in self.api.data:
            ipv4_net = self.api.get_data('ipv4_net')
            if (ipv4_net == False) or (ipv4_net == None):
                interface_obj.ipv4_net = None
            else:
                interface_obj.ipv4_net = DBNetworkBlocksIPv4.objects.get(uuid=ipv4_net)
                
        # IPv6 address / network
        if 'ipv6_addr' in self.api.data:
            interface_obj.ipv6_addr = None if not self.api.data['ipv6_addr'] else self.api.data['ipv6_addr']
        if 'ipv6_net' in self.api.data:
            ipv6_net = self.api.get_data('ipv6_net')
            if (ipv6_net == False) or (ipv6_net == None):
                interface_obj.ipv6_net = None
            else:
                interface_obj.ipv6_net = DBNetworkBlocksIPv6.objects.get(uuid=ipv6_net)
                
        # Update the interface
        interface_obj.save()
      
    def launch(self):
        """
        Worker method for updating a router interface.
        """
        
        # Get a list of authorized routers
        auth_routers = self.api.acl.authorized_objects('net_router')
        
        # If the router doesn't exist or access denied
        if not self.router in auth_routers.ids:
            return invalid('Cannot update interface one router [%s], router not found or access denied' % self.router)
        
        # Extract the router details
        router_details = auth_routers.extract(self.router)
        
        # Make sure the interface exists on the router
        interface_found = False
        for interface in router_details['interfaces']:
            if interface['uuid'] == self.interface:
                interface_found = True
        
        # If the interface is not attached to the router
        if not interface_found:
            return invalid('Cannot update interface [%s] on router [%s], interface not found' % (self.interface, self.router))
        
        # Update the interface
        try:
            self._update_interface()
            
        # Failed to update interface
        except Exception as e:
            return invalid('Failed to update interface: %s' % str(e))
        
        # Successfully updated interface
        return valid('Successfully updated interface')
      
class NetworkRouterAddInterface:
    """
    Add an interface to an existing router.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Interface UUID
        self.uuid = str(uuid4())
        
        # Target router / router object
        self.router = self.api.acl.target_object()
        self.router_obj = None
        
        # Attributes
        self.name = self.api.get_data('name')
        self.desc = self.api.get_data('desc')
        self.hwaddr = self.api.get_data('hwaddr')
        self.ipv4_net = self.api.get_data('ipv4_net')
        self.ipv4_addr = self.api.get_data('ipv4_addr', None)
        self.ipv6_net = self.api.get_data('ipv6_net')
        self.ipv6_addr = self.api.get_data('ipv6_addr', None)
        
    def _create_interface(self):
        """
        Create the router interface.
        """
        
        # Construct the initial parameters
        params = {
            'uuid': self.uuid,
            'router': self.router_obj,
            'name': self.name,
            'desc': self.desc,
            'hwaddr': self.hwaddr,
            'ipv4_addr': self.ipv4_addr,
            'ipv6_addr': self.ipv6_addr
        }
        
        # If attaching to an IPv4 network
        if self.ipv4_net:
            
            # Get a list of authorized IPv4 network blocks
            auth_ipv4_blocks = self.api.acl.authorized_objects('net_block_ipv4')
            
            # If the IPv4 block doesn't exist or access denied
            if not self.ipv4_net in auth_ipv4_blocks.ids:
                raise Exception('IPv4 network [%s] not found or access denied' % self.ipv4_net)
            
            # Set the IPv4 network object
            params['ipv4_net'] = DBNetworkBlocksIPv4.objects.get(uuid=self.ipv4_net)
            
        # If attaching to an IPv6 network
        if self.ipv6_net:
            
            # Get a list of authorized IPv6 network blocks
            auth_ipv6_blocks = self.api.acl.authorized_objects('net_block_ipv6')
            
            # If the IPv6 block doesn't exist or access denied
            if not self.ipv6_net in auth_ipv6_blocks.ids:
                raise Exception('IPv6 network [%s] not found or access denied' % self.ipv6_net)
            
            # Set the IPv6 network object
            params['ipv6_net'] = DBNetworkBlocksIPv6.objects.get(uuid=self.ipv6_net)
        
        # Create the router interface
        DBNetworkRouterInterfaces(**params).save()
        
        # Return the parameters
        return params
        
    def launch(self):
        """
        Worker method for adding an interface to a router.
        """
        
        # Get a list of authorized routers
        auth_routers = self.api.acl.authorized_objects('net_router')
        
        # If the router doesn't exist or access denied
        if not self.router in auth_routers.ids:
            return invalid('Cannot add interface to router [%s], not found or access denied' % self.router)
        
        # Get the router object
        self.router_obj = DBNetworkRouters.objects.get(uuid=self.router)
        
        # Create the interface
        try:
            params = self._create_interface()
            
        # Failed to add interface
        except Exception as e:
            return invalid('Failed to add interface to router [%s]: %s' % (self.router, str(e)))
        
        # Construct the web response data
        web_data = {
            'uuid': self.uuid,
            'name': params['name'],
            'desc': params['desc'],
            'hwaddr': params['hwaddr'],
            'ipv4_net': None,
            'ipv4_addr': params['ipv4_addr'],
            'ipv6_net': None,
            'ipv6_addr': params['ipv6_addr']
        }
        
        # If attaching to an IPv4 network block
        if self.ipv4_net:
            web_data['ipv4_net'] = params['ipv4_net'].uuid
        
        # If attaching to an IPv6 network block
        if self.ipv6_net:
            web_data['ipv6_net'] = params['ipv6_net'].uuid
        
        # Successfully added router interface
        return valid('Successfully created router interface', web_data)
      
class NetworkRouterUpdate:
    """
    Update an existing network router definition.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target router
        self.router = self.api.acl.target_object()
        
    def _update_router(self):
        """
        Update router attributes.
        """
        
        # Get an instance of the router object
        router_obj = DBNetworkRouters.objects.get(uuid=self.router)
        
        # Name
        if 'name' in self.api.data:
            router_obj.name = self.api.data['name']
        
        # Description
        if 'desc' in self.api.data:
            if (self.api.data['desc'] == None) or (self.api.data['desc'] == False):
                router_obj.desc = None
            if self.api.data['desc']:
                router_obj.desc = self.api.data['desc']
                
        # HW Address
        if 'hwaddr' in self.api.data:
            if (self.api.data['hwaddr'] == None) or (self.api.data['hwaddr'] == False):
                router_obj.hwaddr = None
            if self.api.data['hwaddr']:
                router_obj.hwaddr = self.api.data['hwaddr']
        
        # IPv4 Address
        if 'ipv4_addr' in self.api.data:
            if (self.api.data['ipv4_addr'] == None) or (self.api.data['ipv4_addr'] == False):
                router_obj.ipv4_addr = None
            if self.api.data['ipv4_addr']:
                router_obj.ipv4_addr = self.api.data['ipv4_addr']
                
        # IPv6 Address
        if 'ipv6_addr' in self.api.data:
            if (self.api.data['ipv6_addr'] == None) or (self.api.data['ipv6_addr'] == False):
                router_obj.ipv6_addr = None
            if self.api.data['ipv6_addr']:
                router_obj.ipv6_addr = self.api.data['ipv6_addr']
        
        # Datacenter
        if 'datacenter' in self.api.data:
            if (self.api.data['datacenter'] == None) or (self.api.data['datacenter'] == False):
                router_obj.datacenter = None
            if self.api.data['datacenter']:
                
                # Build a list of authorized datacenters
                auth_datacenters = self.api.acl.authorized_objects('datacenter')
                
                # If the target datacenter doesn't exist or access is denied
                if not self.api.data['datacenter'] in auth_datacenters.ids:
                    raise Exception('Could not locate datacenter, not found or access denied')
                
                # Update the datacenter
                router_obj.datacenter = DBDatacenters.objects.get(uuid=self.api.data['datacenter'])
        
        # IPv4 Network
        if 'ipv4_net' in self.api.data:
            if (self.api.data['ipv4_net'] == False) or (self.api.data['ipv4_net'] == None):
                router_obj.ipv4_net = None
            if self.api.data['ipv4_net']:
            
                # Get a list of authorized IPv4 network blocks
                auth_ipv4_blocks = self.api.acl.authorized_objects('net_block_ipv4')
                
                # If the IPv4 block doesn't exist or access denied
                if not self.api.data['ipv4_net'] in auth_ipv4_blocks.ids:
                    raise Exception('IPv4 network [%s] not found or access denied' % self.api.data['ipv4_net'])
                
                # Set the IPv4 network object
                router_obj.ipv4_net = DBNetworkBlocksIPv4.objects.get(uuid=self.api.data['ipv4_net'])
            
        # IPv6 Network
        if 'ipv6_net' in self.api.data:
            if (self.api.data['ipv6_net'] == False) or (self.api.data['ipv6_net'] == None):
                router_obj.ipv6_net = None
            if self.api.data['ipv6_net']:
            
                # Get a list of authorized IPv6 network blocks
                auth_ipv6_blocks = self.api.acl.authorized_objects('net_block_ipv6')
                
                # If the IPv6 block doesn't exist or access denied
                if not self.api.data['ipv6_net'] in auth_ipv6_blocks.ids:
                    raise Exception('IPv6 network [%s] not found or access denied' % self.api.data['ipv6_net'])
                
                # Set the IPv6 network object
                router_obj.ipv6_net = DBNetworkBlocksIPv4.objects.get(uuid=self.api.data['ipv6_net'])
        
        # Metadata
        if 'meta' in self.api.data:
            if (self.api.data['meta'] == None) or (self.api.data['meta'] == False):
                router_obj.meta = None
            if self.api.data['meta']:
                
                # Load the existing metadata
                current_meta = {} if not router_obj.meta else json.loads(router_obj.meta)
                
                # Scan new metadata keys
                for k,v in self.api.data['meta'].iteritems():
                    
                    # If clearing an existing key
                    if (k in current_meta) and (v == False) or (v == None):
                        del current_meta[k]
                        
                    # If adding a new key
                    if not (k in current_meta):
                        current_meta[k] = v
                        
                    # If updating an existing key
                    if (k in current_meta) and current_meta[k]:
                        current_meta[k] = v
            
                # Set the new metadata value
                router_obj.meta = current_meta
                
        # Save the router attributes
        router_obj.save()
        
    def launch(self):
        """
        Worker method for updating an existing network router object.
        """
        
        # Build a list of authorized routers
        auth_routers = self.api.acl.authorized_objects('net_router')
        
        # If the router doesn't exist or access denied
        if not self.router in auth_routers.ids:
            return invalid('Failed to update router [%s], not found or access denied' % self.router)
        
        # Get the router object
        self.router_obj = DBNetworkRouters.objects.get(uuid=self.router)
        
        # Update the router
        try:
            self._update_router()
            
        # Failed to update all attributes
        except Exception as e:
            return invalid('Failed to update router: %s' % str(e))
        
        # Successfully updated router
        return valid('Successfully updated router')
      
class NetworkRouterDelete:
    """
    Delete an existing network router definition.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target router
        self.router = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method for deleting an existing network router object.
        """
        
        # Build a list of authorized routers
        auth_routers = self.api.acl.authorized_objects('net_router')
        
        # If the router doesn't exist or access denied
        if not self.router in auth_routers.ids:
            return invalid('Failed to delete router [%s], not found or access denied' % self.router)
        
        # Extract the router details
        router_details = auth_routers.extract(self.router)
        
        # If the router is attached to any interfaces
        if len(router_details['interfaces']) > 0:
            return invalid('Must remove all interfaces before deleting router')
        
        # Delete the router
        try:
            DBNetworkRouters.objects.get(uuid=self.router).delete()
        
        # Failed to delete router
        except Exception as e:
            return invalid('Failed to delete router: %s' % str(e))
        
        # Successfully deleted router
        return valid('Successfully deleted router', {
            'uuid': self.router
        })
      
class NetworkRouterCreate:
    """
    Create a new network router definition.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Generate a UUID
        self.uuid = str(uuid4())
        
        # Attributes
        self.name = self.api.get_data('name')
        self.desc = self.api.get_data('desc', None)
        self.datacenter = self.api.get_data('datacenter')
        self.hwaddr = self.api.get_data('hwaddr', None)
        self.meta = self.api.get_data('meta', None)
        self.ipv4_addr = self.api.get_data('ipv4_addr', None)
        self.ipv4_net = self.api.get_data('ipv4_net')
        self.ipv6_addr = self.api.get_data('ipv6_addr', None)
        self.ipv6_net = self.api.get_data('ipv6_net')
        
    def _create_router(self):
        """
        Create the router object.
        """
        
        # Set the database object parameters
        params = {
            'uuid': self.uuid,
            'name': self.name,
            'desc': self.desc,
            'meta': self.meta,
            'hwaddr': self.hwaddr,
            'ipv4_addr': self.ipv4_addr,
            'ipv6_addr': self.ipv6_addr
        }
        
        # If attaching to an IPv4 network
        if self.ipv4_net:
            
            # Get a list of authorized IPv4 network blocks
            auth_ipv4_blocks = self.api.acl.authorized_objects('net_block_ipv4')
            
            # If the IPv4 block doesn't exist or access denied
            if not self.ipv4_net in auth_ipv4_blocks.ids:
                raise Exception('IPv4 network [%s] not found or access denied' % self.ipv4_net)
            
            # Set the IPv4 network object
            params['ipv4_net'] = DBNetworkBlocksIPv4.objects.get(uuid=self.ipv4_net)
            
        # If attaching to an IPv6 network
        if self.ipv6_net:
            
            # Get a list of authorized IPv6 network blocks
            auth_ipv6_blocks = self.api.acl.authorized_objects('net_block_ipv6')
            
            # If the IPv6 block doesn't exist or access denied
            if not self.ipv6_net in auth_ipv6_blocks.ids:
                raise Exception('IPv6 network [%s] not found or access denied' % self.ipv6_net)
            
            # Set the IPv6 network object
            params['ipv6_net'] = DBNetworkBlocksIPv6.objects.get(uuid=self.ipv6_net)
        
        # Get the datacenter object if applying
        if self.datacenter:
            
            # Build a list of authorized datacenters
            auth_datacenters = self.api.acl.authorized_objects('datacenter')
            
            # If the datacenter doesn't exist or isn't authorized
            if not self.datacenter in auth_datacenters.ids:
                return invalid('Cannot create new router in datacenter [%s], not found or access denied' % self.datacenter)
            
            # Set the datacenter object
            params['datacenter'] = DBDatacenters.objects.get(uuid=self.datacenter)
        
        # Save the router object
        DBNetworkRouters(**params).save()
        
        # Return the parameters
        return params
        
    def launch(self):
        """
        Worker method for creating a new network router object.
        """
        
        # Create the router object
        try:
            params = self._create_router()
            
        # Critical error when creating network router
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create network router: %s' % str(e)))
        
        # Construct the web response data
        web_data = {
            'uuid': self.uuid,
            'name': self.name,
            'desc': self.desc,
            'hwaddr': self.hwaddr,
            'ipv4_addr': self.ipv4_addr,
            'ipv6_addr': self.ipv6_addr
        }
        
        # If attaching to an IPv4 network
        if self.ipv4_net:
            web_data.update({
                'ipv4_net': {
                    'uuid': params['ipv4_net'].uuid,
                    'label': '%s/%s' % (params['ipv4_net'].network, params['ipv4_net'].prefix)
                }
            })
            
        # If attaching to an IPv6 network
        if self.ipv6_net:
            web_data.update({
                'ipv6_net': {
                    'uuid': params['ipv6_net'].uuid,
                    'label': '%s/%s' % (params['ipv6_net'].network, params['ipv6_net'].prefix)
                }
            })
        
        # If attaching to a datacenter
        if self.datacenter:
            web_data.update({
                'datacenter': {
                    'uuid': params['datacenter'].uuid,
                    'name': params['datacenter'].name
                }
            })
        
        # Return the response
        return valid('Successfully created network router', web_data)
      
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
                return invalid('Failed to retrieve router [%s], not found or access denied' % self.router)
            
            # Return the router details
            return valid(json.dumps(auth_routers.extract(self.router)))
            
        # If retrieving all routers
        else:
            return valid(json.dumps(auth_routers.details))