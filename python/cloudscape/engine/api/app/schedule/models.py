from django.db import models

class DBSchedules(models.Model):
    """
    Main database model for storing API schedules.
    """
    
    # Hosts table columns
    uuid         = models.CharField(max_length=36, unique=True)
    name         = models.CharField(max_length=30, unique=True)
    desc         = models.CharField(max_length=256)
    interval     = models.CharField(max_length=16)
    enabled      = models.BooleanField()
    last_run     = models.DateTimeField()
    manifest     = models.TextField()
    
    # Custom model metadata
    class Meta:
        db_table = 'schedules'