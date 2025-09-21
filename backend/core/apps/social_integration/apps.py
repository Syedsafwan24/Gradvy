"""
backend/core/apps/social_integration/apps.py
Social integration app configuration
Handles social media connections, external platform integrations
RELEVANT FILES: models.py, social_services.py, privacy_compliance/
"""

from django.apps import AppConfig


class SocialIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.social_integration'
    verbose_name = 'Social Media & Platform Integration'

    def ready(self):
        """Initialize social integration services when app is ready"""
        # Import signals here to avoid circular imports
        try:
            import apps.social_integration.signals  # noqa
        except ImportError:
            pass
