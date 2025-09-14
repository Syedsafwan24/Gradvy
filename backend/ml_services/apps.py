"""
backend/ml_services/apps.py
Django app configuration for ML services
Configures the ML services as a proper Django application
RELEVANT FILES: __init__.py, tasks.py, services/
"""

from django.apps import AppConfig


class MlServicesConfig(AppConfig):
    """Configuration for ML Services Django app"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_services'
    verbose_name = 'ML Services'

    def ready(self):
        """
        Initialize ML services when Django app is ready

        This method is called when the Django app registry has been populated
        and all models have been imported.
        """
        # Import tasks to register them with Celery
        try:
            from . import tasks
        except ImportError:
            pass  # Tasks may not be available in all environments

        # Initialize ML system if needed
        try:
            from .utils.model_initializer import get_global_initializer
            # Don't initialize here as it may be too early and resource-intensive
            # Initialization happens on-demand in services
        except ImportError:
            pass  # ML components may not be available