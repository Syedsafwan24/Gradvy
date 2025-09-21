"""
backend/core/apps/privacy_compliance/apps.py
Privacy compliance app configuration
Handles GDPR compliance, consent management, data privacy
RELEVANT FILES: models.py, compliance_tasks.py, auth/
"""

from django.apps import AppConfig


class PrivacyComplianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.privacy_compliance'
    verbose_name = 'Privacy & GDPR Compliance'

    def ready(self):
        """Initialize privacy compliance services when app is ready"""
        # Import signals here to avoid circular imports
        try:
            import apps.privacy_compliance.signals  # noqa
        except ImportError:
            pass
