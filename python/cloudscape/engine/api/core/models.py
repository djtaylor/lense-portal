
# Django Libraries
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

PROTO_IPV4 = 'ipv4'
PROTO_IPV6 = 'ipv6'

class NullTextField(models.TextField):
    """
    Custom Django model field for null capable text fields.
    """
    def __init__(self, *args, **kwargs):

        # Allow null/blank values
        self.blank = True
        self.null  = True
        
        # Construct the parent field class
        super(NullTextField, self).__init__(*args, **kwargs)

class NullForeignKey(models.ForeignKey):
    """
    Custom Django model field for null capable foreign key relationships.
    """
    def __init__(self, *args, **kwargs):

        # Allow null/blank values
        self.blank = True
        self.null  = True
        
        # Set to null on delete of parent key
        self.on_delete = models.SET_NULL

        # Construct the parent field class
        super(NullForeignKey, self).__init__(*args, **kwargs)

class NetworkPrefix(models.IntegerField):
    """
    Custom Django model field for IPv4/IPv6 network prefixes.
    """
    def __init__(self, protocol, *args, **kwargs):
        
        # Available protocols
        _protocols = [PROTO_IPV4, PROTO_IPV6]
        
        # Set the protocol
        if not protocol.lower() in _protocols:
            raise ValidationError('Value for attribute <protocol> must be one of: %s' % ','.join(_protocols))
        self.protocol = protocol
        
        # IPv4
        if self.protocol == PROTO_IPV4:
            self.max_length = 2
            self.validators = [MinValueValidator(1), MaxValueValidator(32)]
            
        # IPv6
        if self.protocol == PROTO_IPV6:
            self.max_length = 3
            self.validators = [MinValueValidator(1), MaxValueValidator(128)]
            
        # Construct the parent field class
        super(NetworkPrefix, self).__init__(*args, **kwargs)

class NetworkVLAN(models.IntegerField):
    """
    Custom Django model field for IPv4 VLANs.
    """
    
    def __init__(self, *args, **kwargs):
        self.max_length = 4
        self.validators = [MinValueValidator(0), MaxValueValidator(4095)]
            
        # Construct the parent field class
        super(NetworkVLAN, self).__init__(*args, **kwargs)