import json
import copy
from uuid import uuid4

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.locations.models import DBDatacenters
from cloudscape.engine.api.app.network.models import DBNetworkRouters, DBNetworkBlocksIPv4, DBNetworkBlocksIPv6

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
            'desc': self.attrs['desc'],
            'network': self.attrs['network'],
            'prefix': self.attrs['prefix'],
            'active': self.attrs['active'],
            'locked': self.attrs['locked']
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
        
        # Target router
        self.router = self.api.acl.target_object()
        
        # Router object
        self.router_obj = None
        
        # Update attributes
        self.name = self.api.get_data('name')
        self.desc = self.api.get_data('desc')
        self.datacenter = self.api.get_data('datacenter')
        self.meta = self.api.get_data('meta')
        
    def _update_name(self):
        """
        Update the router name.
        """
        if self.name:
            self.router_obj.name = self.name
        
    def _update_desc(self):
        """
        Update the router description.
        """
        if self.desc:
            self.router_obj.desc = self.desc
        
    def _update_datacenter(self):
        """
        Update the router datacenter.
        """
        
        # If clearing the datacenter
        if (self.datacenter == None) or (self.datacenter == False):
            self.router_obj.datacenter = None
        
        # If changing the datacenter
        if self.datacenter:
            
            # Build a list of authorized datacenters
            auth_datacenters = self.api.acl.authorized_objects('datacenter')
            
            # If the target datacenter doesn't exist or access is denied
            if not self.datacenter in auth_datacenters.ids:
                raise Exception('Could not locate datacenter, not found or access denied')
            
            # Update the datacenter
            self.router_obj.datacenter = DBDatacenters.objects.get(uuid=self.datacenter)
        
    def _update_meta(self):
        """
        Update the router metdata.
        """
        
        # If clearing the metadata
        if (self.meta == None) or (self.meta == False):
            self.router_obj.meta = None
        
        # If updating the metadata
        if self.meta:
            
            # Load the existing metadata
            current_meta = {} if not self.router_obj.meta else json.loads(self.router_obj.meta)
            
            # Scan new metadata keys
            for k,v in self.meta.iteritems():
                
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
            self.router_obj.meta = current_meta
        
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
        
        # Update name / description / datacenter / metadata
        try:
            self._update_name()
            self._update_desc()
            self._update_datacenter()
            self._update_meta()
            
            # Update the model
            self.router_obj.save()
            
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
        
        # Name / description / datacenter / metadata
        self.name = self.api.get_data('name')
        self.desc = self.api.get_data('desc')
        self.datacenter = self.api.get_data('datacenter')
        self.meta = self.api.get_data('meta')
        
    def launch(self):
        """
        Worker method for creating a new network router object.
        """
        
        # Set the database object parameters
        params = {
            'uuid': self.uuid,
            'name': self.name,
            'desc': self.desc
        }
        
        # If setting metadata
        if self.meta:
            params['meta'] = self.meta
        
        # Get the datacenter object if applying
        if self.datacenter:
            
            # Build a list of authorized datacenters
            auth_datacenters = self.api.acl.authorized_objects('datacenter')
            
            # If the datacenter doesn't exist or isn't authorized
            if not self.datacenter in auth_datacenters.ids:
                return invalid('Cannot create new router in datacenter <%s>, not found or access denied' % self.datacenter)
            
            # Set the datacenter object
            params['datacenter'] = DBDatacenters.objects.get(uuid=self.datacenter)
        
        # Create the router object
        try:
            DBNetworkRouters(**params).save()
            
        # Critical error when creating network router
        except Exception as e:
            return invalid(self.api.log.exception('Failed to create network router: %s' % str(e)))
        
        # Construct the web response data
        web_data = {
            'uuid': self.uuid,
            'name': self.name,
            'desc': self.desc
        }
        
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
                return invalid('Failed to retrieve router <%s>, not found or access denied' % self.router)
            
            # Return the router details
            return valid(json.dumps(auth_routers.extract(self.router)))
            
        # If retrieving all routers
        else:
            return valid(json.dumps(auth_routers.details))