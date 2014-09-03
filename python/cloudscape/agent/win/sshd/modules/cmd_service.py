import wmi
import platform
import win32serviceutil as win32svc

"""
Linux Command Emulator: service

Class used to emulate the 'service' command on Windows machines running the CloudScape
SSH server. Used to manage Windows services.
"""
class ModService:
    def __init__(self, chan):
        
        # WMI instance
        self.wmi      = wmi.WMI()
        
        # Connection channel and shell environment
        self.chan     = chan
        self.shell    = None
        self.command  = None
    
        # Constructed services object
        self.services = {}
    
        # Machine name
        self.machine  = platform.node()
    
        # Service actions
        self.actions  = ['stop', 'start', 'restart', 'status']
    
        # Action mapper
        self.map      = self._mapper()
        
    """ Set Command Modules """
    def set(self, command):
        self.command = command
    
    """ Help Text """
    def help(self):
        return 'Use to manage Windows services - service <name> [start|stop|restart|status] -or- service [list-all|list-running]'
    
    """ Construct Services """
    def _construct_services(self):
        for service in self.wmi.Win32_Service():
            self.services[service.Name] = service
    
    """ Service Entry """
    def _list_service(self, service):
        running = 'yes' if service.Started else 'no'
        entry = '{:30s}  {:9d}  {:^6s}  {:^12s}  {:^7s}'.format(service.Name, service.ProcessID, service.Status, service.StartMode, running)
        return entry
    
    """ Service Header """
    def _list_header(self):
        header = ['']
        header.append('{:^30s}  {:^9s}  {:^6s}  {:^12s}  {:^7s}'.format('             Name             ', '   PID   ', 'Status', '    Mode    ', 'Running'))
        header.append('{:^30s}  {:^9s}  {:^6s}  {:^12s}  {:^7s}'.format('------------------------------', '---------', '------', '------------', '-------'))
        return header
    
    """ List Running Services """
    def _list_running(self):
        self._construct_services()
        
        # Build the services output
        services = self._list_header()
        for name, service in self.services.iteritems():
            if service.Started:
                services.append(self._list_service(service))
        services.append('')
        return services
    
    """ List All Services """
    def _list_all(self):
        self._construct_services()
        
        # Build the services output
        services = self._list_header()
        for name, service in self.services.iteritems():
            services.append(self._list_service(service))
        services.append('')
        return services
    
    """ Start Service """
    def _start(self, service_name):
        try:
            win32svc.StartService(service_name, self.machine)
            return ['Successfully started Windows service \'%s\'' % service_name]
        except Exception as e:
            LOG.exception('Failed to start Windows service \'%s\': %s' % (service_name, str(e)))
            return ['Failed to start Windows service \'%s\'' % service_name]
    
    """ Stop Service """
    def _stop(self, service_name):
        try:
            win32svc.StopService(service_name, self.machine)
            return ['Successfully stopped Windows service \'%s\'' % service_name]
        except Exception as e:
            LOG.exception('Failed to stop Windows service \'%s\': %s' % (service_name, str(e)))
            return ['Failed to stop Windows service \'%s\'' % service_name]
    
    """ Restart Service """
    def _restart(self, service_name):
        try:
            win32svc.RestartService(service_name, self.machine)
            return ['Successfully restarted Windows service \'%s\'' % service_name]
        except Exception as e:
            LOG.exception('Failed to restart Windows service \'%s\': %s' % (service_name, str(e)))
            return ['Failed to restart Windows service \'%s\'' % service_name]
    
    """ Service Status """
    def _status(self, service_name):
        status = self._list_header()
        status.append(self._list_service(self.services[service_name]))
        status.append('')
        return status
    
    """ Action Mapper """
    def _mapper(self):
        return {
            'status':  self._status,
            'start':   self._start,
            'stop':    self._stop,
            'restart': self._restart
        }
    
    """ Run Command """
    def run(self, shell):
        
        # Get an updated shell environment
        self.shell = shell
        
        # Make sure a target service is specified
        if not self.shell['args']:
            self.shell['output'].append('Usage: service <name> [stop|start|restart|status] -or- service [list-all|list-running]')
            return self.shell
        
        # Target service
        target_service = self.shell['args'][0]
        
        # If listing all services
        if target_service == 'list-all':
            self.shell['output'] = self._list_all()
            return self.shell
            
        # If listing running services
        elif target_service == 'list-running':
            self.shell['output'] = self._list_running()
            return self.shell
            
        # If managing a specific service
        else:
            
            # Make sure the target service exists
            if not target_service in self.services:
                self.shell['output'].append('Service \'%s\' not found' % target_service)
                return self.shell
            else:
                
                # Make sure an action is specific
                if len(self.shell['args']) == 1:
                    self.shell['output'].append('Usage: service %s [stop|start|restart|status] -or- service [list-all|list-running]' % target_service)
                    return shell
                
                # Make sure the action is valid
                service_action = self.shell['args'][1]
                if not service_action in self.actions:
                    self.shell['output'].append('Usage: service %s [stop|start|restart|status] -or- service [list-all|list-running]' % target_service)
                    return self.shell
                
                # Construct the services list
                self._construct_services()
                
                # Handle the service action
                self.shell['output'] = self.map[service_action](target_service)
                return self.shell