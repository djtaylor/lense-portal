import time
import json

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.engine.api.app.agent.models import DBHostStats
from cloudscape.engine.api.app.host.models import DBHostFormulas, DBHostDetails, DBHostSystemInfo, DBHostServices

class AgentSync:
    """
    API class used to handle data retrieval from the managed host. The data returned
    is used to make changes on the remote system.
    """
    def __init__(self, parent):
        self.api  = parent
        
        # Target host
        self.host = self.api.data['uuid']
        
    def launch(self):
        """
        Worker method for sending synchronized data to the managed host.
        """
        
        # Make sure the host exists
        if not DBHostDetails.objects.filter(uuid=self.host).count():
            return invalid('Cannot retrieve synchronization data, could not locate host <%s> in database' % self.host)
        
        # Get host details
        host_details = DBHostDetails.objects.filter(uuid=self.host).values()[0]
        
        # Retrieve host services
        services     = host_details['sys']['services'] 
        
        # Return the data object
        return valid(json.dumps({
            'services': services
        }))

class AgentSystem:
    """
    API class that handles system information updates from a managed host.
    """
    def __init__(self, parent):
        self.api      = parent

        # Target host
        self.host     = self.api.data['uuid']

        # Target host object
        self.host_obj = None

    def _set_defaults(self):
        """
        Create a default table row if the host's system information row doesn't exist yet.
        """
        if not DBHostSystemInfo.objects.filter(host=self.host).count():
            DBHostSystemInfo(
                host      = self.host_obj,
                network   = '[]',
                firewall  = '{}',
                partition = '[]',
                memory    = '{}',
                disk      = '[]',
                cpu       = '{}',
                os        = '{}'
            ).save()

    def _set_services(self):
        """
        Update service rows for the managed host.
        """
        if 'services' in self.api.data['sys']:
            
            # Extract the services data
            services_data = self.api.data['sys']['services']
            
            # Updated services / existing services
            services_new = [x['name'] for x in services_data]
            services_cur = [x['name'] for x in list(DBHostServices.objects.filter(host=self.host).values())]
            
            # Check if the service has been updated
            def service_updated(service):
                for s in services_cur:
                    if s['name'] == service['name']:
                        if (s['state']['active'] != service['state_active']) or (s['state']['target'] != service['state_target']):
                            return True
                        return False
                return True
            
            # Delete any removed services
            for s in services_cur:
                if not s in services_new:
                    
                    # Construct the service filter
                    filter = { 'host_id': self.host, 'name': s }
                    
                    # Delete the removed serviced
                    DBHostServices.objects.filter(**filter).delete()
                    
                    # Log the service removal
                    self.api.log.info('Removing service <%s> entry from host <%s>' % (s['name'], self.host))
            
            # Process each service definition
            for service in services_data:
                
                # If creating a new service
                if not service['name'] in services_cur:
                    DBHostServices(
                        host         = self.host_obj,
                        name         = service['name'],
                        state_active = service['state']['active'],
                        state_target = service['state']['active'],
                        monitor      = False
                    ).save()
                    
                    # Log the service creation
                    self.api.log.info('Creating new service <%s> entry for host <%s>' % (service['name'], self.host))
                    
                # If updating an existing service
                else:
                    
                    # Define the service filter
                    filter = { 'host_id': self.host, 'name': service['name'] }
                    
                    # Define the update parameters
                    update = { 
                        'state_active': service['state']['active'],
                        'state_target': service['state']['target']
                    }
                    
                    # Update the service row if any changes found
                    if service_updated(service):
                        DBHostServices.objects.filter(**filter).update()
                        
                        # Log the service update
                        self.api.log.info('Updating service <%s> entry for host <%s>' % (service['name'], self.host))

    # Update system information
    def launch(self):

        # Make sure the host exists
        if not DBHostDetails.objects.filter(uuid=self.host).count():
            return invalid('Cannot update system information, could not locate host <%s> in database' % self.host)

        # Get the host parent object
        self.host_obj = DBHostDetails.objects.get(uuid=self.host)

        # Make sure the host system information row exists
        self._set_defaults()

        # Get the current system information
        sys_info = DBHostSystemInfo.objects.filter(host=self.host).values()[0]

        # Set the updated database parameters
        db_params = {}
        for key in ['network', 'firewall', 'partition', 'memory', 'disk', 'os', 'cpu']:
            db_params[key] = sys_info[key] if not (key in self.api.data['sys']) else json.dumps(self.api.data['sys'][key])
        
        # Update the host system information
        try:
            
            # Update the host system information table
            DBHostSystemInfo.objects.filter(host=self.host).update(**db_params)
            
            # Update the host services table
            self._set_services()
            
        # Critical error when updating system information
        except Exception as e:
            return invalid('Failed to update host <%s> system information in the database: %s' % (self.host, str(e)))
        
        # Host system information updated
        return valid('Successfully updated host <%s> system information' % self.host)
        
class AgentStatus:
    """
    Update the agent status for a managed host.
    """
    def __init__(self, parent):
        self.api  = parent

        # Target host / agent status
        self.host   = self.api.data['uuid']
        self.status = self.api.data['status']

    # Update the agent status
    def launch(self):
        
        # Make sure the host exists
        if not DBHostDetails.objects.filter(uuid=self.host).count():
            return invalid('Failed to update host <%s> status, could not locate host in database' % self.host)
        
        # Get the current host details
        host_details = DBHostDetails.objects.filter(uuid=self.host).values()[0]
        
        # Update the agent status
        try:
            DBHostDetails.objects.filter(uuid=self.host).update(agent_status=self.status, last_checkin=time.strftime('%Y-%m-%d %H:%M:%S'))
        
            # Update the host cache
            self.api.cache.save_object('host', self.host)
        
        # Critical error when updating host agent status
        except Exception as e:
            return invalid('Failed to update host <%s> agent status in the database: %s' % (self.host, str(e)))

        # Broadcast the status to web portal clients if the agent status changed
        if host_details['agent_status'] != self.status:
            self.api.socket.broadcast('agent.status', {
                'uuid':   self.host,
                'status': self.status
            })

        # Agent status successfully updated
        return valid('Successfully updated host <%s> agent status to <%s>' % (self.host, self.status))

class AgentFormula:
    """
    A class to manage the formula agent process on any managed hosts. Responsible for
    saving formula run results to the database.
    """
    def __init__(self, parent):
        self.api     = parent
        
        # Target host / formula
        self.host    = self.api.data['sys_uuid']
        self.formula = self.api.data['formula']
        
    def launch(self):
        """
        Worker method used to saving formula run status to the database.
        """
        self.api.log.info('Updating formula <%s> run status for host <%s>' % (self.formula, self.host))
        
        # Check if the formula ID for the specific host is already in the database
        if DBHostFormulas.objects.filter(host=self.host).filter(formula=self.formula).count():
            
            # Filter parameters
            filter = {
                'host':    self.host,
                'formula': self.formula,
                'current': True
            }
            
            # Updating status for a previous formula run
            try:
                DBHostFormulas.objects.filter(**filter).update(
                    formula     = self.formula,
                    exit_status = self.api.data['exit_status'],
                    exit_code   = self.api.data['exit_code'],
                    exit_msg    = self.api.data['exit_msg'],
                    log         = self.api.data['log'])
                return valid('Successfully updated formula <%s> entry for host <%s>' % (self.formula, self.host))
            
            # Critical error when updating host formula entry
            except Exception as e:
                return invalid(self.api.log.exception('Failed to update formula <%s> entry for host <%s>: %s' % (self.formula, self.host, str(e))))
            
        # Setting status for a new formula run
        else:
            
            # Get the parent host details
            host_details = DBHostDetails.objects.get(uuid=self.host)
            
            # Create the new formula status entry
            try:
                DBHostFormulas(
                    id          = None, 
                    host        = host_details,
                    formula     = self.formula,
                    exit_status = self.api.data['exit_status'],
                    exit_code   = self.api.data['exit_code'],
                    exit_msg    = self.api.data['exit_msg'],
                    log         = self.api.data['log']
                ).save()
                
                # Formula run status update success
                return valid('Successfully updated formula <%s> run status for host <%s>' % (self.formula, self.host))
            
            # Critical error when creating host formula entry
            except Exception as e:
                return invalid(self.api.log.exception('Failed to create formula <%s> entry for host <%s>: %s' % (self.formula, self.host, str(e))))
        
class AgentPoll:
    """
    API class responsible for uploading polling statistics for managed hosts.
    """
    def __init__(self, parent):
        self.api = parent
        
    def launch(self):
        """
        Worker method used to upload the polling data to the host statistics table.
        """

        # Construct the database object
        data = json.dumps(self.api.data['poll'])
        data = {
            'uptime':     self.api.data['poll']['uptime'],
            'memory_use': json.dumps(self.api.data['poll']['memory_use']),
            'memory_top': json.dumps(self.api.data['poll']['memory_top']),
            'cpu_use':    json.dumps(self.api.data['poll']['cpu_use']),
            'disk_use':   json.dumps(self.api.data['poll']['disk_use']),
            'disk_io':    json.dumps(self.api.data['poll']['disk_io']),
            'network_io': json.dumps(self.api.data['poll']['network_io'])
        }
        self.api.log.info('Uploading poll data for \'%s\' to host database' % self.api.data['uuid'])
        
        # Upload the polling data
        if not DBHostStats(self.api.data['uuid']).create(data):
            return invalid('Failed to save host \'%s\' statistics, see the server log for errors' % self.api.data['uuid'])
        return valid('Successfully uploaded polling data for host \'%s\'' % self.api.data['uuid'])