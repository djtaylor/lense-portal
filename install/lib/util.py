# Feedback / collection / configuration objects
Feedback   = None
Collection = None
config     = None

class CloudScapeUtils(object):
    def __init__(self):
        
        # Access internal CloudScape modules
        sys.path.append('../python')
        
        # Make the import variables global
        global Feedback, Collection, config
        
        # Import the modules into the global namespace
        from cloudscape.common.feedback import Feedback
        from cloudscape.common.collection import Collection
        import cloudscape.common.config as config
        
        # Module instances
        self.fb = Feedback()
        self.collection = Collection()
        self.config = config