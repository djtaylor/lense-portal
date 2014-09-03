
# CloudScape Libraries
from cloudscape.common.vars import SYS_TYPE, LOG_DIR, SSH_AUTHKEYS, np
from cloudscape.common import config
from cloudscape.common.collection import Collection

# Log configuration section
CONFIG_LOG = {
    'service':         np('%s/service.log' % LOG_DIR),
    'agent':           np('%s/agent.log' % LOG_DIR),
    'sshd':            np('%s/sshd.log' % LOG_DIR)
}

# Agent configuration section
CONFIG_AGENT = {
    'log':             np('%s/agent.log' % LOG_DIR),
    'uuid':            None,
    'api_key':         None,
    'interval':        10
}

# SSH server configuration (Windows only)
CONFIG_SSHD  = {
    'port':            19500,
    'address':         '',
    'authorized_keys': SSH_AUTHKEYS
}

# System configuration
CONFIG_SYS   = {
    'distro':          None,
    'version':         None,
    'arch':            None
}

# API server configuration
CONFIG_API   = {
    'host':            None,
    'proto':           None,
    'port':            None
}

"""
Windows Agent Configuration

Configuration wrapper for the main configuration parser. Looks through the raw object
parsed from the agent configuration, and sets any default values required. Returns
a namedtuple object.
"""
class AgentConfig:
    def __init__(self):
    
        # Load the configuration file
        self.conf_i = config.parse()
        
        # Supported configuration and default mappings
        self.conf_d = {
            'log':    CONFIG_LOG,
            'agent':  CONFIG_AGENT,
            'ssh':    CONFIG_SSHD,
            'sys':    CONFIG_SYS,
            'server': CONFIG_API
        } 
        
        # Linux doesn't use the SSH block
        if SYS_TYPE == 'linux':
            self.conf_d.pop('ssh', None)
        
        # Parsed and constructed configuration
        self.conf_p = self._parse()
        
    """ Tuple Contains Check """
    def _tuple_contains(self, tuple, section, option):
        if not tuple:
            return False
        if not section in tuple._fields:
            return False
        if not option in tuple.__getattribute__(section)._fields:
            return False
        return tuple.__getattribute__(section).__getattribute__(option)
        
    """ Parse Configuration """
    def _parse(self):
        config_obj = {}
        for section, options in self.conf_d.iteritems():
            if not hasattr(self.conf_i, section):
                config_obj[section] = options
            else:
                config_obj[section] = {}
                for option, def_value in options.iteritems():
                    opt_value = self._tuple_contains(self.conf_i, section, option)
                    if not opt_value:
                        opt_value = def_value
                    config_obj[section][option] = opt_value
        return Collection(config_obj).get()
        
    """ Get Configuration """
    def get(self):
        return self.conf_p