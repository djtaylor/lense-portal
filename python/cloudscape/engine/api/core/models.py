import json

# Django Libraries
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

class JSONField(models.TextField):
    """
    Custom Django model field for storing JSON data strings.
    """
    
    # Enable/disable empty string
    empty = False
    
    def __init__(self, empty=False, *args, **kwargs):
        
        # Only accept boolean values for the <empty> attribute
        if not isinstance(empty, bool):
            raise ValidationError('JSONField model keyword <empty> must be either true or false')
        
        # Empty values flag
        self.empty = empty
        
        # If empty JSON values are allowed
        if self.empty:
            kwargs['blank'] = True
            kwargs['null']  = True
        
        # Construct the parent field
        super(TextField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, connection):
        """
        Convert the JSON string to an object when returning.
        """
        
        # If the value is empty, return null
        if value is None:
            return value
        
        # If a string is set, load it into a JSON object
        return json.loads(value)

    def get_db_prep_value(self, value):
        """
        Except both an object and a string. Make sure both are in valid JSON
        format and return a string.
        """
        
        # If the value is empty
        if not value:
            if not self.empty == True:
                raise ValidationError('JSONField value cannot be empty, must set the model\'s <empty> attribute to true to enable')
            return None
        
        # If the data type is invalid
        if not isinstance(value, list) or isinstance(value, dict) or isinstance(value, str):
            raise ValidationError('JSONField value invalid data %s, only accepts <dict>, <list>, or <str>' % repr(type(value)))
        
        # If saving a list or dictionary
        if isintance(value, list) or isinstance(value, dict):
            
            # Make sure the object is valid JSON
            try:
                json_str = json.dumps(value)
                
                # Return the string value
                return json_str
                
            # Invalid format
            except Exception as e:
                raise ValidationError('JSONField value of %s cannot be converted to JSON string: %s' % (repr(type(value)), str(e)))
            
        # If saving a string
        if isinstance(value, str):
        
            # Make sure the string can be converted to a valid JSON object
            try:
                json_obj = json.loads(value)
                
                # Return the string value
                return value
            
            # Invalid format
            except Exception as e:
                raise ValidationError('JSONField value of %s cannot be converted to JSON object: %s' % (repr(type(value)), str(e)))

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
        _proto_ipv4 = 'ipv4'
        _proto_ipv6 = 'ipv6'
        _protocols  = [_proto_ipv4, _proto_ipv6]
        
        # Set the protocol
        if not protocol in _protocols:
            raise ValidationError('Value for attribute <protocol> must be one of: %s' % ','.join(_protocols))
        
        # IPv4
        if protocol == _proto_ipv4:
            kwargs['max_length'] = 2
            kwargs['validators'] = [MinValueValidator(1), MaxValueValidator(32)]
            
        # IPv6
        if protocol == _proto_ipv6:
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