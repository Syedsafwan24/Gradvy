"""
Django settings module for Gradvy project.

This module automatically loads the appropriate settings based on the environment.
"""

import os
from decouple import config

# Determine which settings to use
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *

# Override with local settings if they exist
try:
    from .local import *
except ImportError:
    pass