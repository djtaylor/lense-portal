#!/usr/bin/env python
import os
import sys

# Lense API Django project management
if __name__ == "__main__":
    
    # Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lense.portal.ui.core.settings")
    
    # Run the application
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
