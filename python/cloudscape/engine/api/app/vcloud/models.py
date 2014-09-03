from django.db import models

"""
VCloud Organizations
"""
class DBVCloudOrg(models.Model):
    
    # VCloud organization table columns
    uuid     = models.CharField(max_length=36, unique=True)
    name     = models.CharField(max_length=30)
    api_href = models.CharField(max_length=256)
    created  = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)    
    
    # Custom model metadata
    class Meta:
        db_table = 'vcloud_org'
        
"""
VCloud VDCs
"""
class DBVCloudVDC(models.Model):
    
    # VCloud VDC table columns
    org      = models.CharField(max_length=36)
    uuid     = models.CharField(max_length=36, unique=True)
    name     = models.CharField(max_length=30)
    api_href = models.CharField(max_length=256)
    rel      = models.CharField(max_length=30)
    created  = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)    
    
    # Custom model metadata
    class Meta:
        db_table = 'vcloud_vdc'
        
"""
VCloud VMs
"""
class DBVCloudVM(models.Model):
    
    # VCloud VM table columns
    org      = models.CharField(max_length=36)
    vdc      = models.CharField(max_length=256)
    uuid     = models.CharField(max_length=36, unique=True)
    name     = models.CharField(max_length=30)
    api_href = models.CharField(max_length=256)
    created  = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)    
    
    # Custom model metadata
    class Meta:
        db_table = 'vcloud_vm'