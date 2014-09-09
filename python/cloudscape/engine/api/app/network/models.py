import sys

# Django Libraries
from django.db import models

# CloudScape Libraries
from cloudscape.engine.api.db.querys import APIQuerySet, APIQueryManager
from cloudscape.engine.api.db.models import NetworkPrefix, NetworkVLAN, NullForeignKey, NullTextField, JSONField
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
    
    # Custom objects manager
    objects      = APIQueryManager(__name__, 'DBNetworkRouterInterfacesQuerySet')
    
    # Custom model metadata
    class Meta:
        db_table = 'network_router_interfaces'

class DBNetworkRouters(models.Model):
    """
    Main database model for storing managed network routers.
    """
    
    # Router columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=128, unique=True)
    desc         = models.CharField(max_length=256)
    datacenter   = NullForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    meta         = JSONField(empty=True)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom objects manager
    objects      = APIQueryManager(__name__, 'DBNetworkRoutersQuerySet')
    
    # Custom model metadata
    class Meta:
        db_table = 'network_routers'

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
    meta         = JSONField(empty=True)
    desc         = models.CharField(max_length=256)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom objects manager
    objects      = APIQueryManager(__name__, 'DBNetworkBlocksQuerySet')
    
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
    meta         = JSONField(empty=True)
    desc         = models.CharField(max_length=256)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom objects manager
    objects      = APIQueryManager(__name__, 'DBNetworkBlocksQuerySet')
    
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
    meta         = JSONField(empty=True)
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
        
class DBNetworkRoutersQuerySet(APIQuerySet):
    """
    Custom queryset manager for the DBNetworkRouters model. This allows customization of 
    the returned QuerySet when extracting router details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(APIQuerySet, self).__init__(*args, **kwargs)
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(DBNetworkRoutersQuerySet, self).values_inner(*fields)
        
        # Extract the router information
        for _i in _r:
            
            # Extract router interfaces
            _i.update({'interfaces': list(DBNetworkRouterInterfaces.objects.filter(router=_i['uuid']).values())})
        
        # Return the constructed router results
        return _r

class DBNetworkBlocksQuerySet(APIQuerySet):
    """
    Custom queryset manager for the IPv4/IPv6 network block models. This allows customization of 
    the returned QuerySet when extracting IP block details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(DBNetworkBlocksQuerySet, self).__init__(*args, **kwargs)
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Return the processed results
        return super(DBNetworkBlocksQuerySet, self).values_inner(*fields)

class DBNetworkRouterInterfacesQuerySet(APIQuerySet):
    """
    Custom queryset manager for network router interfaces.
    """
    def __init__(self, *args, **kwargs):
        super(DBNetworkRouterInterfacesQuerySet, self).__init__(*args, **kwargs)
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Return the processed results
        return super(DBNetworkRouterInterfacesQuerySet, self).values_inner(*fields)