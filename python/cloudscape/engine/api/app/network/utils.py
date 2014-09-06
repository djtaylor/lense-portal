import json
import copy
from uuid import uuid4

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.locations.models import DBDatacenters
from cloudscape.engine.api.app.network.models import DBNetworkRouters
      
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