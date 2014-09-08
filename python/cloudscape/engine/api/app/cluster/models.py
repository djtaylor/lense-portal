from django.db import models

class DBClusterCache(models.Model):
    """
    Database model for storing cached database queries.
    """
    object_type  = models.ForeignKey('auth.DBAuthACLObjects', to_field='type', db_column='object_type')
    object_id    = models.CharField(max_length=36)
    object_data  = models.TextField()
    object_hash  = models.CharField(max_length=32)
    object_size  = models.IntegerField()
    created      = models.DateTimeField(auto_now_add=True)
    modified     = models.DateTimeField(auto_now=True)

    # Custom model metadata
    class Meta:
        db_table = 'cluster_cache'

class DBClusterIndex(models.Model):
    """
    Database model for storing a searchable index of all cluster objects.
    """
    string       = models.CharField(max_length=256)
    label        = models.CharField(max_length=256)
    type         = models.CharField(max_length=32)
    url          = models.CharField(max_length=512)
    
    # Custom model metadata
    class Meta:
        db_table = 'cluster_index'