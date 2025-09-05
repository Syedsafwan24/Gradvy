from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.auth.accounts'
    label = 'accounts'  # Keep the original label for database compatibility

    def ready(self):
        import modules.auth.accounts.signals