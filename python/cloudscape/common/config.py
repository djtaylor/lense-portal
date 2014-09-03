import os.path
import ConfigParser

# CloudScape Libraries
from cloudscape.common.vars import S_CONF, A_CONF, C_BASE
from cloudscape.common.collection import Collection

def _construct(config_file):
    """
    Worker method to construct the named tuple configuration object. Loads
    the configuration using ConfigParser, converts to a dictionary, the to
    a named tuple using the Collection class. Raises an exception if:
    
    1.) The configuration could not be located
    2.) Failed to read the configuration file using ConfigParser
    3.) Failed to parse configuration sections
    
    :rtype: Named tuple of configuration values
    """

    # If the config file does not exist
    if not os.path.isfile(config_file):
        raise Exception('Could not locate configuration file: %s' % (config_file))
    
    # Parse the configuration file
    config = ConfigParser.ConfigParser()
    try:
        config.read(config_file)
    except:
        raise Exception('Failed to parse configuration file: %s' % (config_file))

    # Build a list of configuration sections
    try:
        config_sections = config.sections()
    except:
        raise Exception('Failed to parse configuration sections in: %s' % (config_file))
        
    # Build a dictionary of configuration options
    config_collector = Collection({'base': C_BASE})
    for section in config_sections:
        section_opts = config.options(section)
        
        # Map each section and option to the collection object
        for opt in section_opts:
            map_dict = {section: {opt: config.get(section, opt)}}
            config_collector.map(map_dict)
            
    # Return the collection object
    return config_collector.get()

def parse():
    """
    Parse the configuration file. Detects whether running on the
    server or agent by the presence of each respective file. If the
    server configuration is found, load that. Otherwise, load the
    agent configuration.
    
    :rtype: Named tuple of configuration values
    
    Load the configuration::
        
        # Import the module
        from cloudscape.common import config
        
        # Parse the configuration file
        CONFIG = config.parse()
        
    Accessing configuration values::
    
        # Get the server log file
        print CONFIG.server.log
        
        # Server API port
        print CONFIG.server.port
    """
    
    # Server Configuration
    if os.path.isfile(S_CONF):
        return _construct(S_CONF)
    
    # Agent Configuration
    else:
        return _construct(A_CONF)