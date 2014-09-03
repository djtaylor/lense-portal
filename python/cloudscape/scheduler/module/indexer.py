# CloudScape Libraries
from cloudscape.scheduler.base import ScheduleBase

class ScheduleModule(ScheduleBase):
    """
    Scheduler module for keeping the cluster index up to date.
    """
    def __init__(self):
        super(ScheduleModule, self).__init__(__name__)
        
        # Set the API user for request
        self.set_api(user=self.conf.admin.user, group=self.conf.admin.group)
        
    def launch(self):
        """
        Worker method for running the the schedule indexer.
        """
        while True:
            
            # Make the cluster index rebuild request
            response = self.request(path='cluster', action='index')
            
            # Log the response
            self.log.info('HTTP %s: %s' % (str(response['code']), str(response['body'])))
            
            # Rebuild every minute
            self.time.sleep(60)