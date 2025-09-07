"""
Task management module for Gradvy authentication system.

This module contains Celery tasks and Django signals
for background processing and event handling.
"""

# Import all tasks for Celery autodiscovery
from .tasks import *