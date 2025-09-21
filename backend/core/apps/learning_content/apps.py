"""
backend/core/apps/learning_content/apps.py
Learning content app configuration
Handles course recommendations, content preferences, learning paths
RELEVANT FILES: models.py, recommendation_service.py, ml_services/
"""

from django.apps import AppConfig


class LearningContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.learning_content'
    verbose_name = 'Learning Content & Recommendations'

    def ready(self):
        """Initialize learning content services when app is ready"""
        # Import signals here to avoid circular imports
        try:
            import apps.learning_content.signals  # noqa
        except ImportError:
            pass
