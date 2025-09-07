from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.auth.tasks.tasks import cleanup_user_mfa_data, clean_mfa_data


class Command(BaseCommand):
    help = 'Clean up MFA data for users or run general MFA cleanup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Clean up MFA data for a specific user ID',
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Clean up MFA data for a specific user email',
        )
        parser.add_argument(
            '--general',
            action='store_true',
            help='Run general MFA cleanup (old unconfirmed devices and used backup codes)',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        user_id = options.get('user_id')
        user_email = options.get('user_email')
        general = options.get('general')

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"Cleaning up MFA data for user: {user.email}")
                result = cleanup_user_mfa_data(user_id)
                self.stdout.write(self.style.SUCCESS(f"Success: {result}"))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
                
        elif user_email:
            try:
                user = User.objects.get(email=user_email)
                self.stdout.write(f"Cleaning up MFA data for user: {user.email}")
                result = cleanup_user_mfa_data(user.id)
                self.stdout.write(self.style.SUCCESS(f"Success: {result}"))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with email {user_email} not found"))
                
        elif general:
            self.stdout.write("Running general MFA cleanup...")
            result = clean_mfa_data()
            self.stdout.write(self.style.SUCCESS(f"Success: {result}"))
            
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Please specify either --user-id, --user-email, or --general"
                )
            )
