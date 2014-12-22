import importlib

# CloudScape Libraries
from cloudscape.scheduler.base import ScheduleBase
from cloudscape.engine.api.objects.cache import CacheManager
from cloudscape.engine.api.app.auth.models import DBAuthACLObjects

class ScheduleModule(ScheduleBase):
    """
    Scheduler module for keeping the cluster index up to date.
    """
    def __init__(self):
        super(ScheduleModule, self).__init__(__name__)
        
        # Cache manager
        self.cache = CacheManager()
        
    def _worker(self):
        """
        Internal method for running the cache manager.
        """
        while True:
            self.log.info('Refreshing database cache')
            
            # Build a list of ACL objects
            acl_objects = list(DBAuthACLObjects.objects.all().values())
            
            # Process each ACL object type
            for acl_object in acl_objects:
                obj_type   = acl_object['type']
                
                # Get an instance of the object class
                obj_mod    = importlib.import_module(acl_object['obj_mod'])
                obj_class  = getattr(obj_mod, acl_object['obj_cls'])
                obj_key    = acl_object['obj_key']
                
                # Process and cache each object
                for obj_details in list(obj_class.objects.all().values()):
                    obj_id = obj_details[obj_key]
                    
                    # Update the cache
                    self.cache.save_object(obj_type, obj_id)
            
            # Rebuild cache every minute
            self.time.sleep(60)
        
    def launch(self):
        """
        Worker method for running the the schedule indexer.
        """
        
        # Start the cache worker
        try:
            self._worker()
            
        # Critical error when running cache scheduler
        except Exception as e:
            self.log.exception('Error when running cache scheduler: %s' % str(e))
        