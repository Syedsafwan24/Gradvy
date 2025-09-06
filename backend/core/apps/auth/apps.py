from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth'
    label = 'gradvy_auth'  # Unique label to avoid conflict with django.contrib.auth

    def ready(self):
        try:
            import auth.signals
        except ImportError:
            pass