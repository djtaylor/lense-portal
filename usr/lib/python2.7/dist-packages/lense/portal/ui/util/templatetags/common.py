import json

# Django Libraries
from django import template
from django.utils import six

# Register template tag library
register = template.Library()

@register.simple_tag
def py2js(obj):
    """
    Convert a Python object to a JavaScript value to render on page.
    """
    
    # Undefined
    if obj == None:
        return 'null'
    
    # Boolean values
    if isinstance(obj, bool):
        return 'true' if obj else 'false'
    
    # Integer values
    if isinstance(obj, six.integer_types):
        return obj
    
    # String values
    if isinstance(obj, six.string_types):
        return '"%s"' % obj
    
    # List / dictionary values
    if isinstance(obj, (list, dict)):
        return json.dumps(obj)