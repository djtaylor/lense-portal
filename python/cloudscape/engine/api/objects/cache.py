# coding=utf-8
import sys
import json
import base64
import hashlib
import importlib

# Django Libraries
from django.core.serializers.json import DjangoJSONEncoder

# CloudScape Libraries
from cloudscape.common import config
from cloudscape.common import logger
from cloudscape.engine.api.objects.acl import ACLObjects
from cloudscape.engine.api.app.cluster.models import DBClusterCache

class CacheManager(object):
    """
    API class responsible for caching database queries.
    """
    def __init__(self):
        
        # Configuration / logger objects
        self.conf = config.parse()
        self.log  = logger.create(__name__, self.conf.utils.log)
        
    def get_object(self, obj_type, obj_id=None, decode=True, filters={}):
        """
        Retrieve cached data for an object in the database.
        """
        
        # Object filter parameters
        obj_filter = {
            'object_type': obj_type
        }
        
        # If retrieving a single object
        if obj_id:
            obj_filter['object_id'] = obj_id
        
        # If the object(s) exists
        if DBClusterCache.objects.filter(**obj_filter).count():
            
            # Get the cached data row(s)
            data_rows = list(DBClusterCache.objects.filter(**obj_filter).values())
            
            # If retrieving all objects
            if not obj_id:
                self.log.info('Retrieving cached data for all objects of type <%s>' % obj_type)
                
                # Return object
                cached_data = []
                
                # Process each data row
                for data_row in data_rows:
            
                    # If decoding the data
                    if decode:
                        cached_data.append(json.loads(base64.decodestring(data_row['object_data'])))
                        continue
                    
                    # Append data as a string
                    cached_data.append(data_row['object_data'])
                
                # If filtering data
                if filters:
                    filtered_data = []
                    for data in cached_data:
                        for k,v in filters:
                            if data[k] == v:
                                filtered_data.append(data)
                    cached_data = filtered_data
                
                # Return the cached data
                return cached_data
                
            # If retrieving a single object
            else:
                self.log.info('Retrieved cached data for object <%s> of type <%s>: bytes_cached=%s, decode=%s, hash=%s' % (obj_id, obj_type, str(data_row['object_size'], repr(decode), data_row['object_hash'])))
                
                # Get the cached data
                cached_data = data_rows[0]['object_data']
                
                # If decoding the data
                if decode:
                    return json.loads(base64.decodestring(cached_data))
                
                # Return data as a string
                return cached_data
            
        # Object not found
        else:
            self.log.info('No cached data for object <%s> of type <%s> found' % (obj_id, obj_type))
        
            # Return empty data
            return False
        
    def save_object(self, obj_type, obj_id, values={}):
        """
        Save cache data for an object in the database.
        """
    
        # If the ACL object exists
        if len(ACLObjects.get_values(obj_type)) > 0:
            try:
                
                # If supplied, values argument must be a dictionary
                if values and not isinstance(values, dict):
                    self.log.error('Failed to cache object <%s> of type <%s>, values keyword must contain a dictionary' % (obj_id, obj_type))
                    return False
                
                # Get the ACL object definition
                acl_object = ACLObjects.get(type=obj_type)
        
                # Get an instance of the object class
                obj_mod    = importlib.import_module(getattr(acl_object, 'obj_mod'))
                obj_class  = getattr(obj_mod, getattr(acl_object, 'obj_cls'))
                obj_key    = getattr(acl_object, 'obj_key')
                
                # Create the object filter
                obj_filter = {}
                obj_filter[obj_key] = obj_id
                
                # Define the cache object filter
                cache_filter = {
                    'object_type': obj_type,
                    'object_id':   obj_id
                }
                
                # If the object doesn't exist anymore
                if not obj_class.objects.filter(**obj_filter).count():
                    
                    # If an expired cache entry exists
                    if DBClusterCache.objects.filter(**cache_filter).count():
                        self.log.info('Base object <%s> of type <%s> no longer exists, flushing cached entry' % (obj_id, obj_type))
                        
                        # Flush the old cache entry
                        DBClusterCache.objects.filter(**cache_filter).delete()
                        
                    # Expired cache object cleared
                    return True
                
                # Get the object details
                obj_details = base64.encodestring(json.dumps(list(obj_class.objects.filter(**obj_filter).values(**values))[0], cls=DjangoJSONEncoder))
                obj_size    = sys.getsizeof(obj_details)
                obj_hash    = hashlib.md5(obj_details).hexdigest()
                
                # If the object already has a cache entry
                if DBClusterCache.objects.filter(**cache_filter).count():
                    
                    # Get the current cache entry
                    cache_row = list(DBClusterCache.objects.filter(**cache_filter).values())[0]
                    
                    # If the cached data hasn't changed
                    if cache_row['object_hash'] == obj_hash:
                        return self.log.info('Cached data unchanged for object <%s> of type <%s>' % (obj_id, obj_type))
                    
                    # Update the cached data
                    DBClusterCache.objects.filter(**cache_filter).update(object_data=obj_details, object_size=obj_size)
                    
                # Create a new cache entry
                else:
                
                    # Create the cache entry
                    DBClusterCache(
                        object_type = acl_object,
                        object_id   = obj_id,
                        object_data = obj_details,
                        object_hash = obj_hash,
                        object_size = obj_size
                    ).save()
                
                # Object successfull cached
                self.log.info('Cached data for object <%s> of type <%s>: bytes_cached=%s, hash=%s' % (obj_id, obj_type, str(obj_size), obj_hash))
                
            # Critical error when caching object
            except Exception as e:
                self.log.exception('Failed to cache object <%s> of type <%s>: %s' % (obj_id, obj_type, str(e)))
            
        # ACL object does not exist
        else:
            self.log.error('Cannot cache object <%s> of type <%s>, ACL object type not found' % (obj_id, obj_type))
    
    def flush_object(self, obj_type, obj_id):
        """
        Flush the cache entry for a specific object from the database.
        """
        
        # Filter parameters
        filter = {
            'object_type': obj_type,
            'object_id':   obj_id
        }
        
        # If the object exists
        if DBClusterCache.objects.filter(**filter).count():
            
            # Delete the object cache entry
            DBClusterCache.objects.filter(**filter).delete()
            
            # Successfully flushed object cache
            self.log.info('Successfully flushed cache for object <%s> of type <%s>' % (obj_id, obj_type))
            
        # Object does not exist
        else:
            self.log.error('Failed to flush cache for object <%s> of type <%s>, cache entry not found' % (obj_id, obj_type))
            
    def flush_all(self):
        """
        Flush the entire cache table.
        """
        DBClusterCache.objects.all().delete()