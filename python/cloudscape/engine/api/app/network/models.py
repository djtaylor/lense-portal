from copy import copy

# Django Libraries
from django.db import models

# CloudScape Libraries
from cloudscape.engine.api.core.models import NetworkPrefix, NetworkVLAN, NullForeignKey, NullTextField
from cloudscape.engine.api.app.locations.models import DBDatacenters

class DBNetworkVLANs(models.Model):
    """
    Main database model for storing managed network VLANs.
    """
    
    # VLAN columns
    uuid         = models.CharField(max_length=36, unique=True)
    number       = NetworkVLAN(unique=True)

    # Custom model metadata
    class Meta:
        db_table = 'network_vlans'

class DBNetworkRouterInterfaces(models.Model):
    """
    Main database model for storing router interfaces.
    """
    
    # Router interface columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=64)
    desc         = models.CharField(max_length=256)
    router       = models.ForeignKey('network.DBNetworkRouters', to_field='uuid', db_column='router')
    hwaddr       = models.CharField(max_length=17, unique=True)
    ipv4_net     = NullForeignKey('network.DBNetworkBlocksIPv4', to_field='uuid', db_column='ipv4_net')
    ipv4_addr    = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    ipv6_net     = NullForeignKey('network.DBNetworkBlocksIPv6', to_field='uuid', db_column='ipv6_net')
    ipv6_addr    = models.GenericIPAddressField(protocol='ipv6', blank=True, null=True, unique=True)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_router_interfaces'

class DBNetworkRoutersQuerySet(models.query.QuerySet):
    """
    Custom queryset manager for the DBNetworkRouters model. This allows customization of 
    the returned QuerySet when extracting router details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(DBNetworkRoutersQuerySet, self).__init__(*args, **kwargs)
        
        # Timestamp format
        self.tstamp = '%Y-%m-%d %H:%M:%S'
        
        # Get all datacenters
        self.datacenters = list(DBDatacenters.objects.all().values())
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(DBNetworkRoutersQuerySet, self).values(*fields)
        
        # Extract the router information
        for _i in _r:
            
            # Extract router interfaces
            _i.update({'interfaces': list(DBNetworkRouterInterfaces.objects.filter(router=_i['uuid']).values())})
            
            # Extract datacenter information
            _i.update({
                'datacenter': {
                    'uuid': copy(_i['datacenter_id']),
                    'name': [x['name'] for x in self.datacenters if x['uuid'] == _i['datacenter_id']][0]
                }
            })
            
            # Remove the old datacenter reference
            del _i['datacenter_id']
            
            # Parse the date formats
            _i.update({
                'created':  _i['created'].strftime(self.tstamp),
                'modified': _i['modified'].strftime(self.tstamp),
            })
        
        # Return the constructed router results
        return _r

class DBNetworkRoutersManager(models.Manager):
    """
    Custom objects manager for the DBNetworkRouters model. Acts as a link between the main
    DBNetworkRouters model and the custom DBNetworkRoutersQuerySet model.
    """
    def __init__(self, *args, **kwargs):
        super(DBNetworkRoutersManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return DBNetworkRoutersQuerySet(model=self.model)

class DBNetworkRouters(models.Model):
    """
    Main database model for storing managed network routers.
    """
    
    # Router columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=128, unique=True)
    desc         = models.CharField(max_length=256)
    datacenter   = NullForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom objects manager
    objects      = DBNetworkRoutersManager()
    
    # Custom model metadata
    class Meta:
        db_table = 'network_routers'

class DBNetworkBlocksQuerySet(models.query.QuerySet):
    """
    Custom queryset manager for the IPv4/IPv6 network block models. This allows customization of 
    the returned QuerySet when extracting IP block details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(DBNetworkBlocksQuerySet, self).__init__(*args, **kwargs)
        
        # Timestamp format
        self.tstamp = '%Y-%m-%d %H:%M:%S'
        
        # Get all datacenters / routers
        self.datacenters = list(DBDatacenters.objects.all().values())
        self.routers     = list(DBNetworkRouters.objects.all().values())
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(DBNetworkBlocksQuerySet, self).values(*fields)
        
        # Extract the IP block information
        for _i in _r:
            
            # Extract datacenter information
            _i.update({
                'datacenter': {
                    'uuid': copy(_i['datacenter_id']),
                    'name': [x['name'] for x in self.datacenters if x['uuid'] == _i['datacenter_id']][0]
                }
            })
            
            # Remove the old datacenter reference
            del _i['datacenter_id']
            
            # Extract the router information
            if _i['router_id']:
            
                # Extract datacenter information
                _i.update({
                    'router': {
                        'uuid': copy(_i['router_id']),
                        'name': [x['name'] for x in self.routers if x['uuid'] == _i['router_id']][0]
                    }
                })
                
                # Remove the old datacenter reference
                del _i['router_id']
            
            # No router configured
            else:
                del _i['router_id']
                _i['router'] = None
            
            # Parse the date formats
            _i.update({
                'created':  _i['created'].strftime(self.tstamp),
                'modified': _i['modified'].strftime(self.tstamp),
            })
        
        # Return the constructed IP block results
        return _r

class DBNetworkBlocksManager(models.Manager):
    """
    Custom objects manager for the both IPv4/IPv6 network block models. Acts as a link between the main
    network block models and the custom DBNetworkBlocksQuerySet model.
    """
    def __init__(self, *args, **kwargs):
        super(DBNetworkBlocksManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return DBNetworkBlocksQuerySet(model=self.model)

class DBNetworkBlocksIPv4(models.Model):
    """
    Main database model for storing managed IPv4 network blocks.
    """
    
    # IPv4 network block columns
    uuid         = models.CharField(max_length=36, unique=True)
    network      = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    prefix       = NetworkPrefix(protocol='ipv4')
    datacenter   = NullForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    router       = NullForeignKey('network.DBNetworkRouters', to_field='uuid', db_column='router')
    active       = models.NullBooleanField()
    locked       = models.NullBooleanField()
    meta         = NullTextField()
    desc         = models.CharField(max_length=256)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom objects manager
    objects      = DBNetworkBlocksManager()
    
    # Custom model metadata
    class Meta:
        db_table = 'network_blocks_ipv4'
        
class DBNetworkBlocksIPv6(models.Model):
    """
    Main database model for storing managed IPv6 network blocks.
    """
    
    # IPv6 network block columns
    uuid         = models.CharField(max_length=36, unique=True)
    network      = models.GenericIPAddressField(protocol='ipv6', blank=True, null=True, unique=True)
    prefix       = NetworkPrefix(protocol='ipv6')
    datacenter   = NullForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    router       = NullForeignKey('network.DBNetworkRouters', to_field='uuid', db_column='router')
    active       = models.NullBooleanField()
    locked       = models.NullBooleanField()
    meta         = NullTextField()
    desc         = models.CharField(max_length=256)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom objects manager
    objects      = DBNetworkBlocksManager()
    
    # Custom model metadata
    class Meta:
        db_table = 'network_blocks_ipv6'
        
class DBNetworkSwitches(models.Model):
    """
    Main database model for storing managed network switches.
    """
    
    # Switch columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=128, unique=True)
    desc         = models.CharField(max_length=256)
    datacenter   = NullForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    ipv4_net     = NullForeignKey('network.DBNetworkBlocksIPv4', to_field='uuid', db_column='ipv4_net')
    ipv4_addr    = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    ipv6_net     = NullForeignKey('network.DBNetworkBlocksIPv6', to_field='uuid', db_column='ipv6_net')
    ipv6_addr    = models.GenericIPAddressField(protocol='ipv6', blank=True, null=True, unique=True)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_switches'
        
class DBNetworkSwitchInterfaces(models.Model):
    """
    Main database model for storing network switch interfaces.
    """
    
    # Switch interface columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=64)
    desc         = models.CharField(max_length=256)
    switch       = models.ForeignKey('network.DBNetworkSwitches', to_field='uuid', db_column='switch')
    hwaddr       = models.CharField(max_length=17, unique=True)
    ipv4_net     = NullForeignKey('network.DBNetworkBlocksIPv4', to_field='uuid', db_column='ipv4_net')
    ipv4_addr    = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    ipv6_net     = NullForeignKey('network.DBNetworkBlocksIPv6', to_field='uuid', db_column='ipv6_net')
    ipv6_addr    = models.GenericIPAddressField(protocol='ipv6', blank=True, null=True, unique=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_switch_interfaces'