# coding=utf-8
import importlib

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.engine.api.core.cache import CacheManager
from cloudscape.engine.api.app.auth.models import DBAuthACLObjects

class ObjectsManager(object):
    """
    API class used to retrieve object details. If cache retrieval is enabled, the
    object details will be pulled from the database cache table.
    """
    def __init__(self):
        
        # Configuration / logger objects
        self.conf  = config.parse()
        self.log   = logger.create(__name__, self.conf.utils.log)
        
        # Cache manager
        self.cache = CacheManager()
        
    def _get_from_model(self, obj_type, obj_id, values={}, filters={}):
        """
        Retrieve object details directly from the model.
        
        @param obj_type: The type of object to retrieve
        @type  obj_type: str
        @param obj_id:   The ID of the object to retrieve
        @type  obj_id:   str
        @param values:   Extra parameters to pass to the values QuerySet method
        @type  values:   dict
        """
        self.log.info('Retrieving object data from model: type=%s, id=%s' % (obj_type, repr(obj_id)))
        
        # Get the ACL object definition
        acl_object  = DBAuthACLObjects.objects.get(type=obj_type)
        
        # Get an instance of the object class
        obj_mod     = importlib.import_module(getattr(acl_object, 'obj_mod'))
        obj_class   = getattr(obj_mod, getattr(acl_object, 'obj_cls'))
        obj_key     = getattr(acl_object, 'obj_key')
        
        # Create the object filter
        obj_filter  = {}
        
        # If retrieving a single object
        if obj_id:
            obj_filter[obj_key] = obj_id
        
        # Attempt to retrieve the object
        obj_details = list(obj_class.objects.filter(**obj_filter).filter(**filters).values())
        
        # If the object doesn't exist
        if len(obj_details) == 0:
            return None
        
        # Return the object details
        if len(obj_details) > 1:
            return obj_details
        return obj_details[0]
        
    def get(self, obj_type, obj_id=None, cache=True, values={}, filters={}):
        """
        Retrieve details for an API object.
        
        @param obj_type: The type of object to retrieve
        @type  obj_type: str
        @param obj_id:   The ID of the object to retrieve
        @type  obj_id:   str
        @param cache:    Enable or disable retrieval from the database cache table
        @type  cache:    bool
        @param values:   Extra parameters to pass to the values QuerySet method
        @type  values:   dict
        """
        
        # If the ACL object exists
        if DBAuthACLObjects.objects.filter(type=obj_type).count():
            self.log.info('Retrieving database object: type=%s, id=%s, cache=%s' % (obj_type, repr(obj_id), repr(cache)))
            
            # If retrieving from the database cache table
            if cache:
            
                # Look for object details in the cache
                cached_obj = self.cache.get_object(obj_type, obj_id, filters=filters)
                
                # If cached data found
                if cached_obj:
                    self.log.info('Cached data found for object: type=%s, id=%s' % (obj_type, repr(obj_id)))
                    return cached_obj
                
                # No cached data found, retrieve directly from the object model
                return self._get_from_model(obj_type, obj_id, values=values, filters=filters)
                
            # If querying directly from the database
            else:
                return self._get_from_model(obj_type, obj_id, values=values, filters=filters)
            
        # Invalid ACL object type
        else:
            self.log.error('Failed to retrieve object <%s> of type <%s>, object type not found' % (obj_id, obj_type))
            
            # Return an empty result
            return None