import json

# Django Libraries
from django.db import models
from encrypted_fields import EncryptedTextField

# CloudScape Libraries
from cloudscape.engine.api.app.locations.models import DBDatacenters

class DBHostSystemInfo(models.Model):
    """
    Database model to store system information about a host, including memory, CPU,
    hardware, services, etc.
    """
    
    # Host system information columns
    host         = models.ForeignKey('host.DBHostDetails', to_field='uuid', db_column='host')
    network      = models.TextField()
    firewall     = models.TextField()
    partition    = models.TextField()
    memory       = models.TextField()
    disk         = models.TextField()
    os           = models.TextField()
    cpu          = models.TextField()
    
    # Custom model metadata
    class Meta:
        db_table = 'host_system_info'

class DBHostOwner(models.Model):
    """
    Database model to store host ownership information.
    """
    
    # Host ownership information
    host         = models.ForeignKey('host.DBHostDetails', to_field='uuid', db_column='host')
    owner        = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')

    # Custom model metadata
    class Meta:
        db_table = 'host_ownership'

class DBHostServices(models.Model):
    """
    Database model for storing managed host services. This includes current state, target state
    if changing the service state, and monitoring attributes.
    """
    
    # Host service columns
    host         = models.ForeignKey('host.DBHostDetails', to_field='uuid', db_column='host')
    name         = models.CharField(max_length=128)
    state_active = models.BooleanField()
    state_target = models.BooleanField()
    monitor      = models.BooleanField()
    modified     = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'host_services'

class DBHostQuerySet(models.query.QuerySet):
    """
    Custom queryset manager for the DBHostManager model. This allows customization of the returned
    QuerySet when extracting host details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(DBHostQuerySet, self).__init__(*args, **kwargs)
        
        # Timestamp format
        self.tstamp = '%Y-%m-%d %H:%M:%S'
        
        # System information keys
        self.sysinfo_keys = ['network', 'firewall', 'partition', 'memory', 'disk', 'os', 'cpu']
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(DBHostQuerySet, self).values(*fields)
        
        # Extract the system information
        for _h in _r:
            
            # Extract system information
            _h.update({'sys': self._sysinfo(_h['uuid']), 'last_checkin': _h['last_checkin'].strftime(self.tstamp)})
        
            # Get the group ownership
            _o = DBHostOwner.objects.filter(host=_h['uuid']).values()[0]
            
            # Set the group ownership attributes
            _h.update({
                'owner': {
                    'uuid': _o['owner_id']
                }
            })
        
        # Return the constructed host results
        return _r

    def _sysinfo(self, uuid):
        """
        Extract system information for the queried host/hosts.
        """
        
        # Extract system information
        sys_row  = DBHostSystemInfo.objects.filter(host=uuid).values()[0]
        
        # Extract host services and parse the datetime
        sys_srv  = []
        for srv in list(DBHostServices.objects.filter(host=uuid).values()):
            
            # Convert the modified timestamp to a string
            srv['modified'] = srv['modified'].strftime(self.tstamp)
        
            # Extract the state values
            srv['state']    = {
                'active': srv['state_active'],
                'target': srv['state_target']
            }
            
            # Delete the old service keys (messy)
            del srv['state_active']
            del srv['state_target']
            
            # Append the constructed service
            sys_srv.append(srv)
        
        # Load the JSON data for system information
        sys_info = {k:json.loads(sys_row[k]) for k in self.sysinfo_keys}

        # Merge host services
        sys_info['services'] = sys_srv
        
        # Return the system information
        return sys_info

class DBHostManager(models.Manager):
    """
    Custom objects manager for the DBHostDetails model. Acts as a link between the main DBHostDetails
    model and the custom DBHostQuerySet model.
    """
    def __init__(self, *args, **kwargs):
        super(DBHostManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return DBHostQuerySet(model=self.model)

class DBHostDetails(models.Model):
    """
    Main database model for storing host details. Defines the host UUID which links
    the host to a number of other database models.
    """
    
    # Hosts table columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=30)
    ip           = models.CharField(max_length=15, unique=True)
    ssh_port     = models.IntegerField()
    user         = models.CharField(max_length=32)
    os_type      = models.CharField(max_length=16)
    agent_status = models.CharField(max_length=32)
    last_checkin = models.DateTimeField(auto_now=True)
    datacenter   = models.CharField(max_length=36)
    is_virtual   = models.NullBooleanField()
    
    # Custom objects manager
    objects      = DBHostManager()
    
    # Custom model metadata
    class Meta:
        db_table = 'host_details'
    
class DBHostGroups(models.Model):
    """
    Database model used to keep track of host groups that have either been created
    automatically via group formula runs, or manually by an administrator.
    """
    
    # Host groups table columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=30)
    formula      = models.CharField(max_length=64, null=True, blank=True)
    metadata     = models.TextField()
    
    # Custom model metadata
    class Meta:
        db_table = 'host_groups'

class DBHostGroupMembers(models.Model):
    """
    Database model to keep track of hosts that are members of specific groups found
    in the DBHostGroups model.
    """
    
    # Host groups table columns
    host         = models.ForeignKey(DBHostDetails, to_field='uuid', db_column='host')
    group        = models.ForeignKey(DBHostGroups, to_field='uuid', db_column='group')
    
    # Custom model metadata
    class Meta:
        db_table = 'host_group_members'
    
class DBHostFormulas(models.Model):
    """
    Database model used to keep track of formulas that have been applied to hosts. Also
    contains the log files from the formula runs, as well as runtime parameters.
    """
    
    # Host formulas table columns
    host        = models.ForeignKey(DBHostDetails, to_field='uuid', db_column='host')
    formula     = models.CharField(max_length=128)
    exit_status = models.CharField(max_length=32)
    exit_code   = models.IntegerField()
    exit_msg    = models.CharField(max_length=256)
    requires    = models.TextField(null=True, blank=True)
    run_params  = EncryptedTextField()
    log         = models.TextField()
    created     = models.DateTimeField(auto_now_add=True)
    modified    = models.DateTimeField(auto_now=True)
    current     = models.BooleanField()
    
    # Custom model metadata
    class Meta:
        db_table = 'host_formulas'
      
class DBHostDKeys(models.Model):
    """
    Database model that contains deployment keys used to activate Windows machines that
    have the CloudScape agent software. Contains an encrypted public/private SSH keypair
    as well as a UUID and identifying name.
    """
        
    # Windows host deployment keys
    uuid     = models.CharField(max_length=36, unique=True)
    name     = models.CharField(max_length=12, unique=True)
    default  = models.BooleanField()
    pub_key  = EncryptedTextField()
    priv_key = EncryptedTextField()
    
    # Custom model metadata
    class Meta:
        db_table = 'host_dkeys'
        
class DBHostSSHAuth(models.Model):
    """
    Database model to contain the encrypted public/private SSH keypair for the cloudscape
    agent user on a managed host.
    """
    
    # Host SSH authentication table columns
    host     = models.ForeignKey(DBHostDetails, to_field='uuid', db_column='host')
    pub_key  = EncryptedTextField()
    priv_key = EncryptedTextField()
    
    # Custom model metadata
    class Meta:
        db_table = 'host_ssh_auth'
   
class DBHostAPIKeys(models.Model):
    """
    Database model that contains the API keys for managed hosts.
    """
    
    # Host API key table columns
    host     = models.ForeignKey(DBHostDetails, to_field='uuid', db_column='host')
    api_key  = models.CharField(max_length=64, unique=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'host_api_keys'
        
class DBHostAPITokens(models.Model):
    """
    Database model that contains API tokens for managed hosts.
    """
    
    # Host API token table columns
    host     = models.ForeignKey(DBHostDetails, to_field='uuid', db_column='host')
    token    = models.CharField(max_length=255, unique=True)
    expires  = models.DateTimeField()
    
    # Custom model metadata
    class Meta:
        db_table = 'host_api_tokens'