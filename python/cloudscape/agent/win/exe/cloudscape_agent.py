import os
import sys
import time
import copy
import socket
import win32event
import win32service
import servicemanager
import win32evtlogutil
import multiprocessing
import win32serviceutil

# CloudScape Libraries
from cloudscape.common import logger
from cloudscape.agent.win.process import Process
from cloudscape.agent.common.config import AgentConfig
from cloudscape.agent.win.base import AgentHandler
from cloudscape.common.utils import CmdEmbedded

""" Agent Command Handler """
def agent_embedded():
    agent = AgentHandler(copy.copy(sys.argv))
    agent.main()

""" Embedded Command Processor """
CMD = CmdEmbedded(sys.argv)
CMD.set_embedded({
    'exec-py':  agent_embedded,
    'exec-win': agent_embedded,
    'exec-pkg': agent_embedded,
    'sysinfo':  agent_embedded,
})

# Process embedded commands
if CMD.is_embedded():
    h = CMD.get_embedded()
    h()
    sys.exit(0)

"""
Windows Service Class
"""
class AgentService(win32serviceutil.ServiceFramework):
    _svc_name_         = 'CloudScapeAgent'
    _svc_display_name_ = 'CloudScape Agent'
    _svc_description_  = 'The CloudScape agent, used to handle receiving commands from the CloudScape API server' \
                         'and sending updates back to the API server.'
    
    # Process properties
    PROC_NAME          = 'cloudscape-agent'
    PROC_MODULE        = 'cloudscape.agent.win.base'
    PROC_CLASS         = 'AgentHandler'
    PROC_METHOD        = 'start'
    
    # Configuration and logger
    CONFIG             = AgentConfig().get()
    LOG                = logger.create('cloudscape.agent.win.service', CONFIG.log.service)
    
    # Class constructor
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        
        # Process manager
        self.process = Process(
            proc_name   = self.PROC_NAME,
            proc_module = self.PROC_MODULE,
            proc_class  = self.PROC_CLASS,
            proc_method = self.PROC_METHOD
        )
        
    """ Stop Service """
    def SvcStop(self):
        self.LOG.info('[%s]: Stopping CloudScape API agent...' % self.PROC_NAME)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # Stop the process
        self.process.stop()
        win32event.SetEvent(self.hWaitStop)
        
    """ Start Service """
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        
        # Start all subprocesses
        self.main()
        
        # Wait for the stop signal and log when stopped
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        win32evtlogutil.ReportEvent(self._svc_name_,
            servicemanager.PYS_SERVICE_STOPPED,
            0,
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            (self._svc_name_, '')
        )
        
    """ Service Handler """
    def main(self):
        
        # Start the process
        self.LOG.info('[%s]: Starting CloudScape API agent...' % self.PROC_NAME)
        self.LOG.info('[%s]: > Process module - \'%s\'' % (self.PROC_NAME, self.PROC_MODULE))
        self.LOG.info('[%s]: > Process class - \'%s\'' % (self.PROC_NAME, self.PROC_CLASS))
        self.LOG.info('[%s]: > Process method - \'%s\'' % (self.PROC_NAME, self.PROC_METHOD))
        self.process.start()
        
# Invoke service
if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AgentService)