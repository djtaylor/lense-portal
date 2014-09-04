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

    # Bool values
    bool_values = ['True', 'False']

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
            
            # If parsing a boolean value
            if config.get(section, opt) in bool_values:
                config_collector.map({section: {opt: config.getboolean(section, opt)}})
                
            # If parsing a string value
            else:
                config_collector.map({section: {opt: config.get(section, opt)}})
            
    # Return the collection object
    return config_collector.get()

def parse(file=None):
    """
    Parse the configuration file. Detects whether running on the
    server or agent by the presence of each respective file. If the
    server configuration is found, load that. Otherwise, load the
    agent configuration.
    """
    
    # If manually specifying a file
    if file:
        return _construct(file)
    
    # Server Configuration
    if os.path.isfile(S_CONF):
        return _construct(S_CONF)
    
    # Agent Configuration
    else:
        return _construct(A_CONF)