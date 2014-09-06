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
        self.uuid = uuid4()
        
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
            DBNetworkRouter(
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
      
class DatacenterDelete:
    """
    Delete an existing datacenter entry.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target datacenter
        self.datacenter = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method used to delete an existing datacenter.
        """
        
        # Build a list of authorized datacenters
        authorized_datacenters = self.api.acl.authorized_objects('datacenter')
        
        # If the datacenter doesnt exist
        if not DBDatacenters.objects.filter(uuid=self.datacenter).count():
            return invalid('Failed to delete datacenter <%s>, not found in database' % self.datacenter)
        
        # If access is not authorized
        if not self.datacenter in authorized_datacenters.ids:
            return invalid('Failed to delete datacenter <%s>, access denied' % self.datacenter)
        
        # Make sure no hosts are in the datacenter
        if DBHostDetails.objects.filter(datacenter=self.datacenter).count():
            return invalid('Cannot delete datacenter <%s> without removing all member hosts')
        
        # Delete the datacenter
        DBDatacenters.objects.filter(uuid=self.datacenter).delete()
        
        # Return the response
        return valid('Successfully deleted datacenter', {
            'uuid': self.datacenter                                                 
        })
    
class DatacenterUpdate:
    """
    Update an existing datacenter entry.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target datacenter
        self.datacenter = self.api.acl.target_object()
        
    def launch(self):
        """
        Worker method used to update an existing datacenter.
        """
        
        # Build a list of authorized datacenters
        authorized_datacenters = self.api.acl.authorized_objects('datacenter')
        
        # If the datacenter doesnt exist
        if not DBDatacenters.objects.filter(uuid=self.datacenter).count():
            return invalid('Failed to update datacenter <%s>, not found in database' % self.datacenter)
        
        # If access is not authorized
        if not self.datacenter in authorized_datacenters.ids:
            return invalid('Failed to update datacenter <%s>, access denied' % self.datacenter)
        
        # Set the update parameters
        params = copy.copy(self.api.data)
        del params['uuid']
        
        # Update the database entry
        DBDatacenters.objects.filter(uuid=self.datacenter).update(**params)
        
        # Return the response
        return valid('Successfully updated datacenter', self.api.data)
        
class DatacenterCreate:
    """
    Create a new datacenter entry.
    """
    def __init__(self, parent):
        self.api = parent
        
    def launch(self):
        """
        Worker method used to create a new datacenter.
        """
        
        # Check if the datacenter already exists
        if DBDatacenters.objects.filter(name=self.api.data['name']).count():
            return invalid('Failed to create datacenter <%s>, already exists' % self.api.data['name'])
        
        # Generate a UUID for the datacenter
        uuid = str(uuid4())
        
        # Create the datacenter
        DBDatacenters(
            uuid  = uuid,
            name  = self.api.data['name'],
            label = self.api.data['label']
        ).save()
        
        # Return the response
        return valid('Successfully created datacenter', {
            'uuid':  uuid,
            'name':  self.api.data['name'],
            'label': self.api.data['label']
        })
        
class DatacenterGet:
    """
    Retrieve either a single datacenter or a list of datacenters.
    """
    def __init__(self, parent):
        self.api           = parent
    
        # Target datacenter / authorized datacenters / authorized hosts
        self.datacenter    = self.api.acl.target_object()
        self.d_authorized  = self.api.acl.authorized_objects('datacenter')
        self.h_authorized  = self.api.acl.authorized_objects('host', 'host/get')
    
    def _get_details(self, datacenter):
        """
        Extract details for the datacenter.
        """
        
        # Get a list of all hosts in the datacenter
        datacenter['hosts'] = [x['uuid'] for x in self.h_authorized.details if x['datacenter'] == datacenter['uuid']]
        
        # Return the update datacenter
        return datacenter
    
    def launch(self):
        """
        Worker method used to retrieve datacenter details.
        """
        
        # If retrieving all datacenters
        if not self.datacenter:
                
            # Return the datacenters object
            return valid(json.dumps([self._get_details(x) for x in self.d_authorized.details]))
            
        # Retrieve a single datacenter
        else:
            
            # Extract the datacenter
            datacenter_details = authorized_datacenters.extract(self.datacenter)
            
            # If the datacenter doesn't exist
            if not datacenter_details:
                return invalid('Could not locate datacenter <%s> in the database' % self.datacenter)
            
            # Return the constructed datacenter object
            return valid(self._get_details(datacenter_details))