import importlib

# Django Libraries
from django.db import models

# CloudScape Libraries
from cloudscape.engine.api.app.locations.models import DBDatacenters
from cloudscape.engine.api.app.schedule.models import DBSchedules
from cloudscape.engine.api.app.formula.models import DBFormulaDetails
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostDKeys, DBHostGroups, DBHostFormulas
from cloudscape.engine.api.app.network.models import DBNetworkRouters, DBNetworkSwitches, DBNetworkBlocksIPv4, DBNetworkBlocksIPv6, DBNetworkVLANs

class DBAuthACLAccessGlobal(models.Model):
    """
    Main database model for global ACL keys. These are ACL keys which are not
    attached to a specific object or limited to a specific group type.
    """
    acl        = models.ForeignKey('auth.DBAuthACLKeys', to_field='uuid', db_column='acl')
    utility    = models.ForeignKey('auth.DBAuthUtilities', to_field='uuid', db_column='utility')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_access_global'

class DBAuthACLAccessObject(models.Model):
    """
    Main database model for object ACL keys. These are ACL keys which are used
    for defining granular permissions for objects, such as hosts or formulas.
    """
    acl        = models.ForeignKey('auth.DBAuthACLKeys', to_field='uuid', db_column='acl')
    utility    = models.ForeignKey('auth.DBAuthUtilities', to_field='uuid', db_column='utility')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_access_object'
        
class DBAuthACLAccessHost(models.Model):
    """
    Main database model for host ACL keys. These are keys which define what resources
    hosts my access using their respective API keys.
    """
    acl        = models.ForeignKey('auth.DBAuthACLKeys', to_field='uuid', db_column='acl')
    utility    = models.ForeignKey('auth.DBAuthUtilities', to_field='uuid', db_column='utility')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_access_host'

class DBAuthUtilities(models.Model):
    """
    Main database model for storing API utility details.
    """
    uuid       = models.CharField(max_length=36, unique=True)
    path       = models.CharField(max_length=128, unique=True)
    desc       = models.CharField(max_length=256)
    method     = models.CharField(max_length=4)
    mod        = models.CharField(max_length=128)
    cls        = models.CharField(max_length=64, unique=True)
    utils      = models.TextField()
    rmap       = models.TextField()
    object     = models.CharField(max_length=64, null=True, blank=True)
    object_key = models.CharField(max_length=32, null=True, blank=True)
    protected  = models.NullBooleanField()
    enabled    = models.BooleanField()
    locked     = models.NullBooleanField()
    locked_by  = models.CharField(max_length=64, null=True, blank=True)
    
    # Custom table metadata
    class Meta:
        db_table = 'utilities'
     
class DBAuthACLObjectsQuerySet(models.query.QuerySet):
    """
    Custom queryset manager for the DBAuthACLObjects model. This allows customization of the returned
    QuerySet when extracting host details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(DBAuthACLObjectsQuerySet, self).__init__(*args, **kwargs)
        
        # Detailed object list
        self._detailed = False
        
    def _extract(self, acl_object):
        """
        Extract object details.
        """
           
        # If not extracting object details
        if not self._detailed:
            return acl_object
            
        # Get an instance of the object class
        obj_mod   = importlib.import_module(acl_object['obj_mod'])
        obj_class = getattr(obj_mod, acl_object['obj_cls'])
        obj_key   = acl_object['obj_key']
        
        # Define the detailed objects container
        acl_object['objects'] = []
        for obj_details in list(obj_class.objects.all().values()):
            
            # Host objects
            if acl_object['type'] == 'host':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name'],
                    'label': '%s - %s %s %s' % (obj_details['ip'], obj_details['sys']['os']['distro'], obj_details['sys']['os']['version'], obj_details['sys']['os']['arch'])           
                })
                
            # Formula objects
            if acl_object['type'] == 'formula':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name'],
                    'label': obj_details['label']            
                })
                
            # Deployment key objects
            if acl_object['type'] == 'dkey':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name']            
                })
                
            # Host group objects
            if acl_object['type'] == 'hgroup':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name']            
                })
                
            # API user objects
            if acl_object['type'] == 'user':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['username'],
                    'label': obj_details['email']              
                })
                
            # API group objects
            if acl_object['type'] == 'group':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name'],
                    'label': obj_details['desc']            
                })
                
            # Datacenter objects
            if acl_object['type'] == 'datacenter':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name'],
                    'label': obj_details['label']      
                })
        
            # Utility objects
            if acl_object['type'] == 'utility':
                acl_object['objects'].append({
                    'id':    obj_details[obj_key],
                    'name':  obj_details['name'],
                    'label': obj_details['name']
                })
        
        # Return the detailed ACL object
        return acl_object
        
    def values(self, detailed=False, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Set the detailed results flag
        self._detailed = detailed
        
        # Store the initial results
        _r = super(DBAuthACLObjectsQuerySet, self).values(*fields)
        
        # ACL return object
        _a = []
        
        # Process each ACL object definition
        for acl_object in _r:
            _a.append(self._extract(acl_object))
        
        # Return the constructed ACL results
        return _a
        
class DBAuthACLObjectsManager(models.Manager):
    """
    Custom objects manager for the DBAuthACLObjects model. Acts as a link between the main DBAuthACLObjects
    model and the custom DBAuthACLObjectsQuerySet model.
    """
    def __init__(self, *args, **kwargs):
        super(DBAuthACLObjectsManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return DBAuthACLObjectsQuerySet(model=self.model)

class DBAuthACLObjects(models.Model):
    """
    Main database model for storing ACL object types.
    """
    type       = models.CharField(max_length=36, unique=True)
    name       = models.CharField(max_length=36)
    acl_mod    = models.CharField(max_length=128)
    acl_cls    = models.CharField(max_length=64, unique=True)
    acl_key    = models.CharField(max_length=36)
    obj_mod    = models.CharField(max_length=128)
    obj_cls    = models.CharField(max_length=64)
    obj_key    = models.CharField(max_length=36)
    def_acl    = models.ForeignKey('auth.DBAuthACLKeys', to_field='uuid', db_column='def_acl', null=True, blank=True, on_delete=models.SET_NULL)

    # Custom objects manager
    objects    = DBAuthACLObjectsManager()

    # Custom table metadata
    class Meta:
        db_table = 'acl_objects'

class DBAuthACLKeysQuerySet(models.query.QuerySet):
    """
    Custom queryset manager for the DBHostManager model. This allows customization of the returned
    QuerySet when extracting host details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(DBAuthACLKeysQuerySet, self).__init__(*args, **kwargs)
        
        # ACL object types / utilities
        self.obj_types = self._get_objects()
        self.utilities = {x['uuid']: x for x in list(DBAuthUtilities.objects.all().values())}
        
    def _get_objects(self):
        """
        Construct ACL object types and definitions.
        """
        
        # Query all ACL object types
        acl_objects = list(DBAuthACLObjects.objects.all().values())
        
        # Construct and return the definition
        return {
            'types':   [x['type'] for x in acl_objects],
            'details': {x['type']: x for x in acl_objects},
        }
        
    def _extract_utilities(self, utilities):
        """
        Extract utility information from an ACL utility assignment.
        """
        
        # ACL utlities return object
        utilities_obj = []
        
        # Object type
        obj_type      = None
        
        # Construct the ACL utilities object
        for util in utilities:
            util_uuid = util['utility_id']
            utilities_obj.append({
                'uuid':   self.utilities[util_uuid]['uuid'],
                'name':   self.utilities[util_uuid]['name'],
                'desc':   self.utilities[util_uuid]['desc'],
                'method': self.utilities[util_uuid]['method'],
                'object': self.utilities[util_uuid]['object']
            })
            
            # If the object type is defined
            obj_type = obj_type if not self.utilities[util_uuid]['object'] else self.utilities[util_uuid]['object']
            
        # Return the ACL utilities object and object type
        return utilities_obj, obj_type
        
    def _extract(self, acl):
        """
        Extract and construct each ACL definition.
        """
        
        # Extract all utility access definitions
        object_util = self._extract_utilities(list(DBAuthACLAccessObject.objects.filter(acl=acl['uuid']).values()))
        global_util = self._extract_utilities(list(DBAuthACLAccessGlobal.objects.filter(acl=acl['uuid']).values()))
        host_util   = self._extract_utilities(list(DBAuthACLAccessHost.objects.filter(acl=acl['uuid']).values()))
        
        # Contstruct the utilities for each ACL access type
        acl['utilities'] = {
            'host':   {
                'type': host_util[1],
                'list': host_util[0]
            },
            'object': {
                'type': object_util[1],
                'list': object_util[0]
            },
            'global': {
                'type': global_util[1],
                'list': global_util[0]
            }          
        }
        
        # Return the constructed ACL object
        return acl
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(DBAuthACLKeysQuerySet, self).values(*fields)
        
        # ACL return object
        _a = []
        
        # Process each ACL definition
        for acl in _r:
            _a.append(self._extract(acl))
        
        # Return the constructed ACL results
        return _a

class DBAuthACLKeysManager(models.Manager):
    """
    Custom objects manager for the DBAuthACLKeys model. Acts as a link between the main DBAuthACLKeys
    model and the custom DBAuthACLKeysQuerySet model.
    """
    def __init__(self, *args, **kwargs):
        super(DBAuthACLKeysManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return DBAuthACLKeysQuerySet(model=self.model)

class DBAuthACLKeys(models.Model):
    """ 
    Main database model for storing ACL keys and details. Each ACL can handle
    authorization for any number of utilities.
    """
    uuid        = models.CharField(max_length=36, unique=True)
    name        = models.CharField(max_length=128, unique=True)
    desc        = models.CharField(max_length=128)
    type_object = models.BooleanField()
    type_host   = models.BooleanField()
    type_global = models.BooleanField()
    
    # Custom objects manager
    objects     = DBAuthACLKeysManager()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_keys'
    
class DBAuthACLGroupObjectGroupPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for group objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    group      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='group', related_name='group_target')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner', related_name='group_owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_group_permissions'
    
class DBAuthACLGroupObjectUserPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for group objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    user       = models.ForeignKey('user.DBUser', to_field='uuid', db_column='user')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_user_permissions'
    
class DBAuthACLGroupObjectHostGroupPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for host group objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    hgroup     = models.ForeignKey(DBHostGroups, to_field='uuid', db_column='hgroup')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_hgroup_permissions'
    
class DBAuthACLGroupObjectDkeyPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for deployment key objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    dkey       = models.ForeignKey(DBHostDKeys, to_field='uuid', db_column='dkey')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_dkey_permissions'
        
class DBAuthACLGroupObjectFormulaPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for formula objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    formula    = models.ForeignKey(DBFormulaDetails, to_field='uuid', db_column='formula')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_formula_permissions'
        
class DBAuthACLGroupObjectDatacenterPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for datacenter objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    datacenter = models.ForeignKey(DBDatacenters, to_field='uuid', db_column='datacenter')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_datacenter_permissions'
        
class DBAuthACLGroupObjectUtilityPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for utility objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    utility    = models.ForeignKey(DBAuthUtilities, to_field='uuid', db_column='utility')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
        
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_utility_permissions'
        
class DBAuthACLGroupObjectHostPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for host objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    host       = models.ForeignKey(DBHostDetails, to_field='uuid', db_column='host')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_host_permissions'
        
class DBAuthACLGroupObjectNetworkRouterPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for network router objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    router     = models.ForeignKey(DBNetworkRouters, to_field='uuid', db_column='router')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_network_router_permissions'
        
class DBAuthACLGroupObjectNetworkSwitchPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for network switch objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    switch     = models.ForeignKey(DBNetworkSwitches, to_field='uuid', db_column='switch')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_network_switch_permissions'
        
class DBAuthACLGroupObjectNetworkBlockIPv4Permissions(models.Model):
    """
    Main database model for storing object ACL permissions for network IPv4 block objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    block      = models.ForeignKey(DBNetworkBlocksIPv4, to_field='uuid', db_column='block')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_network_ipv4_block_permissions'
        
class DBAuthACLGroupObjectNetworkBlockIPv6Permissions(models.Model):
    """
    Main database model for storing object ACL permissions for network IPv6 block objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    block      = models.ForeignKey(DBNetworkBlocksIPv6, to_field='uuid', db_column='block')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_network_ipv6_block_permissions'
        
class DBAuthACLGroupObjectNetworkVLANPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for network VLAN objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    vlan       = models.ForeignKey(DBNetworkVLANs, to_field='uuid', db_column='vlan')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_network_vlan_permissions'
        
class DBAuthACLGroupGlobalPermissions(models.Model):
    """
    Main database model for storing global ACL permissions for groups.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_global_permissions'
