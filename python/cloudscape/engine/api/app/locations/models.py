from django.db import models

class DBDatacenters(models.Model):
    """
    Main database model for storing datacenter locations.
    """
    
    # Hosts table columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=30, unique=True)
    label        = models.CharField(max_length=128)
    metadata     = models.TextField()
    
    # Custom model metadata
    class Meta:
        db_table = 'datacenters'