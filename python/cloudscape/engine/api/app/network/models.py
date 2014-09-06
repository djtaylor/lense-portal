from django.db import models

# CloudScape Libraries
from cloudscape.engine.api.core.models import NetworkPrefix, NetworkVLAN
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

class DBNetworkRouters(models.Model):
    """
    Main database model for storing managed network routers.
    """
    
    # Router columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=128, unique=True)
    desc         = models.CharField(max_length=256)
    datacenter   = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
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
    datacenter   = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    router       = models.ForeignKey('network.DBNetworkRouters', to_field='uuid', db_column='router')
    active       = models.NullBooleanField()
    locked       = models.NullBooleanField()
    meta         = models.TextField()
    desc         = models.CharField(max_length=256)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
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
    datacenter   = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    active       = models.NullBooleanField()
    locked       = models.NullBooleanField()
    meta         = models.TextField()
    desc         = models.CharField(max_length=256)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_blocks_ipv6'

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
    ipv4_net     = models.ForeignKey('network.DBNetworkBlocksIPv4', to_field='uuid', db_column='ipv4_net', blank=True, null=True)
    ipv4_addr    = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    ipv6_net     = models.ForeignKey('network.DBNetworkBlocksIPv6', to_field='uuid', db_column='ipv6_net', blank=True, null=True)
    ipv6_addr    = models.GenericIPAddressField(protocol='ipv6', blank=True, null=True, unique=True)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_router_interfaces'
        
class DBNetworkSwitches(models.Model):
    """
    Main database model for storing managed network switches.
    """
    
    # Switch columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=128, unique=True)
    desc         = models.CharField(max_length=256)
    datacenter   = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    ipv4_net     = models.ForeignKey('network.DBNetworkBlocksIPv4', to_field='uuid', db_column='ipv4_net', blank=True, null=True)
    ipv4_addr    = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    ipv6_net     = models.ForeignKey('network.DBNetworkBlocksIPv6', to_field='uuid', db_column='ipv6_net', blank=True, null=True)
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
    ipv4_net     = models.ForeignKey('network.DBNetworkBlocksIPv4', to_field='uuid', db_column='ipv4_net', blank=True, null=True)
    ipv4_addr    = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    ipv6_net     = models.ForeignKey('network.DBNetworkBlocksIPv6', to_field='uuid', db_column='ipv6_net', blank=True, null=True)
    ipv6_addr    = models.GenericIPAddressField(protocol='ipv6', blank=True, null=True, unique=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_switch_interfaces'