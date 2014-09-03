import json
import copy
from uuid import uuid4

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.schedule.models import DBSchedules
        
class ScheduleGet:
    """
    Retrieve either a single schedule or a list of schedules.
    """
    def __init__(self, parent):
        self.api           = parent
    
        # Target datacenter / authorized datacenters / authorized hosts
        self.schedule     = self.api.acl.target_object()
        self.s_authorized = self.api.acl.authorized_objects('schedule')
    
    def launch(self):
        """
        Worker method used to retrieve schedule details.
        """
        
        # If retrieving all schedules
        if not self.schedule:
                
            # Return the datacenters object
            return valid(json.dumps(self.s_authorized.details))
            
        # Retrieve a single schedule
        else:
            
            # Extract the schedule
            schedule_details = self.s_authorized.extract(self.schedule)
            
            # If the schedule doesn't exist
            if not schedule_details:
                return invalid('Could not locate schedule <%s> in the database' % self.schedule)
            
            # Return the constructed schedule object
            return valid(schedule_details)