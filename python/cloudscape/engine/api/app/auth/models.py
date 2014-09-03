import importlib

# Django Libraries
from django.db import models

# CloudScape Libraries
from cloudscape.engine.api.app.locations.models import DBDatacenters
from cloudscape.engine.api.app.schedule.models import DBSchedules
from cloudscape.engine.api.app.formula.models import DBFormulaDetails
from cloudscape.engine.api.app.host.models import DBHostDetails, DBHostDKeys, DBHostGroups, DBHostFormulas

class DBAuthACLEndpointsGlobal(models.Model):
    """
    Main database model for global ACL keys. These are ACL keys which are not
    attached to a specific object or limited to a specific group type.
    """
    acl        = models.ForeignKey('auth.DBAuthACLKeys', to_field='uuid', db_column='acl')
    endpoint   = models.ForeignKey('auth.DBAuthEndpoints', to_field='uuid', db_column='endpoint')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_endpoints_global'

class DBAuthACLEndpointsObject(models.Model):
    """
    Main database model for object ACL keys. These are ACL keys which are used
    for defining granular permissions for objects, such as hosts or formulas.
    """
    acl        = models.ForeignKey('auth.DBAuthACLKeys', to_field='uuid', db_column='acl')
    endpoint   = models.ForeignKey('auth.DBAuthEndpoints', to_field='uuid', db_column='endpoint')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_endpoints_object'
        
class DBAuthACLEndpointsHost(models.Model):
    """
    Main database model for host ACL keys. These are keys which define what resources
    hosts my access using their respective API keys.
    """
    acl        = models.ForeignKey('auth.DBAuthACLKeys', to_field='uuid', db_column='acl')
    endpoint   = models.ForeignKey('auth.DBAuthEndpoints', to_field='uuid', db_column='endpoint')
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_endpoints_host'

class DBAuthEndpoints(models.Model):
    """
    Main database model for storing endpoint details.
    """
    uuid       = models.CharField(max_length=36, unique=True)
    name       = models.CharField(max_length=128, unique=True)
    desc       = models.CharField(max_length=256)
    path       = models.CharField(max_length=64)
    action     = models.CharField(max_length=16)
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
        db_table = 'endpoints'
     
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
        
            # Endpoint objects
            if acl_object['type'] == 'endpoint':
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
        
        # ACL object types / endpoints
        self.obj_types = self._get_objects()
        self.endpoints = {x['uuid']: x for x in list(DBAuthEndpoints.objects.all().values())}
        
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
        
    def _extract_endpoints(self, endpoints):
        """
        Extract endpoint information from an ACL endpoint assignment.
        """
        
        # ACL endpoints return object
        endpoints_obj = []
        
        # Object type
        obj_type      = None
        
        # Construct the ACL endpoints object
        for ep in endpoints:
            ep_uuid = ep['endpoint_id']
            endpoints_obj.append({
                'uuid':   self.endpoints[ep_uuid]['uuid'],
                'name':   self.endpoints[ep_uuid]['name'],
                'desc':   self.endpoints[ep_uuid]['desc'],
                'method': self.endpoints[ep_uuid]['method'],
                'object': self.endpoints[ep_uuid]['object']
            })
            
            # If the object type is defined
            obj_type = obj_type if not self.endpoints[ep_uuid]['object'] else self.endpoints[ep_uuid]['object']
            
        # Return the ACL endpoints object and object type
        return endpoints_obj, obj_type
        
    def _extract(self, acl):
        """
        Extract and construct each ACL definition.
        """
        
        # Extract all endpoints
        object_ep = self._extract_endpoints(list(DBAuthACLEndpointsObject.objects.filter(acl=acl['uuid']).values()))
        global_ep = self._extract_endpoints(list(DBAuthACLEndpointsGlobal.objects.filter(acl=acl['uuid']).values()))
        host_ep   = self._extract_endpoints(list(DBAuthACLEndpointsHost.objects.filter(acl=acl['uuid']).values()))
        
        # Contstruct the endpoints for each ACL
        acl['endpoints'] = {
            'host':   {
                'type': host_ep[1],
                'list': host_ep[0]
            },
            'object': {
                'type': object_ep[1],
                'list': object_ep[0]
            },
            'global': {
                'type': global_ep[1],
                'list': global_ep[0]
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
    authorization for any number of endpoints.
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
    user       = models.ForeignKey('user.DBUserDetails', to_field='username', db_column='user')
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
       
class DBAuthACLGroupObjectSchedulePermissions(models.Model):
    """
    Main database model for storing object ACL permissions for schedule objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    schedule   = models.ForeignKey(DBSchedules, to_field='uuid', db_column='schedule')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
    
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_schedule_permissions'
        
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
        
class DBAuthACLGroupObjectEndpointPermissions(models.Model):
    """
    Main database model for storing object ACL permissions for endpoint objects.
    """
    acl        = models.ForeignKey(DBAuthACLKeys, to_field='uuid', db_column='acl')
    endpoint   = models.ForeignKey(DBAuthEndpoints, to_field='uuid', db_column='endpoint')
    owner      = models.ForeignKey('group.DBGroupDetails', to_field='uuid', db_column='owner')
    allowed    = models.NullBooleanField()
        
    # Custom table metadata
    class Meta:
        db_table = 'acl_group_object_endpoint_permissions'
        
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
