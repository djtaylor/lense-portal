
# Django Libraries
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

class NullTextField(models.TextField):
    """
    Custom Django model field for null capable text fields.
    """
    def __init__(self, *args, **kwargs):

        # Allow null/blank values
        kwargs['blank'] = True
        kwargs['null']  = True
        
        # Construct the parent field class
        super(NullTextField, self).__init__(*args, **kwargs)

class NullForeignKey(models.ForeignKey):
    """
    Custom Django model field for null capable foreign key relationships.
    """
    def __init__(self, *args, **kwargs):

        # Allow null/blank values
        kwargs['blank'] = True
        kwargs['null']  = True
        
        # Set to null on delete of parent key
        kwargs['on_delete'] = models.SET_NULL

        # Construct the parent field class
        super(NullForeignKey, self).__init__(*args, **kwargs)

class NetworkPrefix(models.IntegerField):
    """
    Custom Django model field for IPv4/IPv6 network prefixes.
    """
    def __init__(self, protocol, *args, **kwargs):
        
        # Available protocols
        _protocols = ['ipv4', 'ipv6']
        
        # Set the protocol
        if not protocol in _protocols:
            raise ValidationError('Value for attribute <protocol> must be one of: %s' % ','.join(_protocols))
        
        # IPv4
        if protocol == PROTO_IPV4:
            kwargs['max_length'] = 2
            kwargs['validators'] = [MinValueValidator(1), MaxValueValidator(32)]
            
        # IPv6
        if protocol == PROTO_IPV6:
            kwargs['max_length'] = 3
            kwargs['validators'] = [MinValueValidator(1), MaxValueValidator(128)]
            
        # Construct the parent field class
        super(NetworkPrefix, self).__init__(*args, **kwargs)

class NetworkVLAN(models.IntegerField):
    """
    Custom Django model field for IPv4 VLANs.
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 4
        kwargs['validators'] = [MinValueValidator(0), MaxValueValidator(4095)]
            
        # Construct the parent field class
        super(NetworkVLAN, self).__init__(*args, **kwargs)