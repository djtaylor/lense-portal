import json
from django.db import models

class DBFormulaTemplates(models.Model):
    """
    Database model for storing formula templates.
    """
    
    # Formula template columns
    formula       = models.ForeignKey('formula.DBFormulaDetails', to_field='uuid', db_column='formula')
    template_name = models.CharField(max_length=128)
    template_file = models.TextField()
    size          = models.IntegerField()
    created       = models.DateTimeField(auto_now_add=True)
    modified      = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'formula_templates'

class DBFormulaQuerySet(models.query.QuerySet):
    """
    Custom queryset manager for the DBFormulaDetails model. This allows customization of the returned
    QuerySet when extracting formula details from the database.
    """
    def __init__(self, *args, **kwargs):
        super(DBFormulaQuerySet, self).__init__(*args, **kwargs)
        
        # Timestamp format
        self.tstamp = '%Y-%m-%d %H:%M:%S'
        
    def _extract(self, formula):
        """
        Extract formula details and templates.
        """
        
        # Stringify each entry
        for k,v in formula.iteritems():
            formula[k] = str(v)
        
        # Get formula templates
        formula['templates'] = [x['template_name'] for x in list(DBFormulaTemplates.objects.filter(formula=formula['uuid']).values())]

        # Extract the manifest
        formula['manifest']  = json.loads(formula['manifest'])

        # Return the updated formula
        return formula
        
    def values(self, *fields):
        """
        Wrapper for the default values() method.
        """
        
        # Store the initial results
        _r = super(DBFormulaQuerySet, self).values(*fields)
        
        # Extract the formula details
        for _f in _r:
            _f = self._extract(_f)
        
        # Return the constructed formula results
        return _r

class DBFormulaManager(models.Manager):
    """
    Custom objects manager for the DBFormulaDetails model. Acts as a link between the main DBFormulaDetails
    model and the custom DBFormulaQuerySet model.
    """
    def __init__(self, *args, **kwargs):
        super(DBFormulaManager, self).__init__()
    
    def get_queryset(self, *args, **kwargs):
        """
        Wrapper method for the internal get_queryset() method.
        """
        return DBFormulaQuerySet(model=self.model)

"""
CloudScape Deployment Formula
"""
class DBFormulaDetails(models.Model):
    
    # Formulas table columns
    uuid       = models.CharField(max_length=36, unique=True)
    name       = models.CharField(max_length=128, unique=True)
    label      = models.CharField(max_length=128)
    desc       = models.TextField()
    manifest   = models.TextField()
    type       = models.CharField(max_length=24)
    internal   = models.NullBooleanField()
    locked     = models.NullBooleanField()
    locked_by  = models.CharField(max_length=64, null=True, blank=True)
    created    = models.DateTimeField(auto_now_add=True)
    modified   = models.DateTimeField(auto_now=True)
    
    # Custom objects manager
    objects    = DBFormulaManager()
    
    # Custom model metadata
    class Meta:
        db_table = 'formula_details'
       
"""
CloudScape Formula Events
"""
class DBFormulaEvents(models.Model):
   
   # Formula template columns
    event_id      = models.CharField(max_length=128)
    event_meta    = models.TextField()
    created       = models.DateTimeField(auto_now_add=True)
    modified      = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'formula_events'
        
"""
CloudScape Formula Runtime Registry
"""
class DBFormulaRegistry(models.Model):
    
    # Formula registry columns
    formula     = models.CharField(max_length=128)
    uuid        = models.CharField(max_length=36, unique=True)
    host        = models.CharField(max_length=36)
    checksum    = models.CharField(max_length=64)
    key         = models.CharField(max_length=64)
    verified    = models.BooleanField()
    decrypted   = models.BooleanField()
    created     = models.DateTimeField(auto_now_add=True)
    modified    = models.DateTimeField(auto_now=True)
    
    # Custom model metadata
    class Meta:
        db_table = 'formula_registry'