# CloudScape Libraries
from cloudscape.scheduler.base import ScheduleBase
from cloudscape.common.vars import A_STOPPED, A_RUNNING

class ScheduleModule(ScheduleBase):
    """
    Scheduler module for keeping the cluster index up to date.
    """
    def __init__(self):
        super(ScheduleModule, self).__init__(__name__)
        
        # Set the API user for request
        self.set_api(user=self.conf.admin.user, group=self.conf.admin.group)
        
        # Time format string / current timestamp
        self.tformat = '%Y-%m-%d %H:%M:%S'
        self.now     = None
        
    def _agent_down(self, uuid):
        """
        Mark a host agent as down if marked as running and last check-in was over
        60 seconds ago.
        """
        
        # Mark the host agent as down
        response = self.request(path='agent', action='status', data={
            'uuid':   uuid,
            'status': A_STOPPED
        })
        
        # Log the response
        self.log.info('HTTP %s: %s' % (response['code'], str(response['body']))) 
        
    def _check_agent(self, host):
        """
        Compare the last check-in date to the current timestamp for hosts where the agent
        is marked as running.
        """
        if host['agent_status'] == A_RUNNING:
                
            # Get the last check-in time
            last_checkin = self.datetime.datetime.strptime(host['last_checkin'], self.tformat)
            
            # Calculate the difference in seconds
            diff_seconds = abs((self.now - last_checkin).seconds)
        
            # If the last check-in was more then 60 seconds ago
            if int(diff_seconds) > 60:
                self.log.info('Last check-in time <%s> for host <%s> agent more then 60 seconds ago, marking agent as stopped' % (host['last_checkin'], host['uuid']))
                self._agent_down(host['uuid'])
        
    def launch(self):
        """
        Worker method for running the the schedule indexer.
        """
        while True:
            
            # Retrieve a list of all hosts
            response = self.request(path='host', action='get')
            
            # If the request failed
            if not response['code'] == 200:
                return self.log.error('HTTP %s: %s' % (response['code'], str(response['body'])))
            
            # Load the hosts
            all_hosts = response['body']
            
            # Get the current datetime
            self.now = self.datetime.datetime.strptime(self.time.strftime(self.tformat), self.tformat)
            
            # Process each host
            for host in all_hosts:
                self.log.info('Processing host: <%s:%s>' % (host['name'], host['uuid']))
                
                # Monitor the host agent
                self._check_agent(host)
            
            # Monitor every 30 seconds
            self.time.sleep(30)