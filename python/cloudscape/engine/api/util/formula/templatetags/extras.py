import re
import json

# Django Libraries
from django import template

# CloudScape Libraries
from cloudscape.common.utils import obj_extract

# Register template tag library
register = template.Library()

@register.simple_tag
def extract(obj, id=None, filter=None):
    return obj_extract(obj, id, filter)