from django.db import models

# CloudScape Libraries
from cloudscape.engine.api.app.locations.models import DBDatacenters

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

class DBNetworkRouterInterfaces(models.Model):
    """
    Main database model for storing router interfaces.
    """
    
    # Router interface columns
    name         = models.CharField(max_length=64)
    desc         = models.CharField(max_length=256)
    router       = models.ForeignKey(DBRouters, to_field='uuid', db_column='router')
    hwaddr       = models.CharField(max_length=17, unique=True)
    ipv4_net     = models.ForeignKey(DBNetworkBlocksIPv4, to_field='uuid', db_column='ipv4_net', blank=True, null=True)
    ipv4_addr    = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    ipv6_addr    = models.GenericIPAddressField(protocol='ipv6', blank=True, null=True, unique=True)
    ipv6_net     = models.ForeignKey(DBNetworkBlocksIPv6, to_field='uuid', db_column='ipv6_net', blank=True, null=True)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_router_interfaces'

class DBNetworkBlocksIPv4(models.Model):
    """
    Main database model for storing managed IPv4 network blocks.
    """
    
    # IPv4 network block columns
    uuid         = models.CharField(max_length=36, unique=True)
    network      = models.GenericIPAddressField(protocol='ipv4', blank=True, null=True, unique=True)
    prefix       = models.CharField(max_length=2)
    datacenter   = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    router       = models.ForeignKey(DBRouters, to_field='uuid', db_column='router')
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
    prefix       = models.CharField(max_length=3)
    datacenter   = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    router       = models.ForeignKey(DBRouters, to_field='uuid', db_column='router')
    active       = models.NullBooleanField()
    locked       = models.NullBooleanField()
    meta         = models.TextField()
    desc         = models.CharField(max_length=256)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
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
    datacenter   = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    router       = models.ForeignKey(DBRouters, to_field='uuid', db_column='router')
    ipv4_net     = models.ForeignKey(DBNetworkBlocksIPv4, to_field='uuid', db_column='ipv4_net', blank=True, null=True)
    ipv6_net     = models.ForeignKey(DBNetworkBlocksIPv6, to_field='uuid', db_column='ipv6_net', blank=True, null=True)
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'network_switches'