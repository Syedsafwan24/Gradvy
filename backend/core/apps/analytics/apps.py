"""
backend/core/apps/analytics/apps.py
Analytics app configuration
Handles user behavior tracking, learning analytics, and AI insights
RELEVANT FILES: models.py, tasks.py, ml_services/
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    verbose_name = 'User Analytics & Behavioral Tracking'

    def ready(self):
        """Initialize analytics services when app is ready"""
        # Import signals here to avoid circular imports
        try:
            import apps.analytics.signals  # noqa
        except ImportError:
            pass
