from celery import shared_task
import time

@shared_task
def send_welcome_email(user_email):
    """
    A sample task to simulate sending a welcome email.
    """
    print(f"Simulating sending welcome email to {user_email}...")
    time.sleep(5) # Simulate a long-running operation
    print(f"Welcome email sent to {user_email}!")
    return f"Email sent to {user_email}"

@shared_task
def process_user_data(user_id):
    """
    A sample task to process user data in the background.
    """
    print(f"Processing data for user ID: {user_id}...")
    time.sleep(10) # Simulate a more intensive operation
    print(f"Finished processing data for user ID: {user_id}.")
    return f"Data processed for user ID: {user_id}"

@shared_task
def clean_mfa_data():
    """
    Cleans up old unconfirmed TOTP devices and used backup codes.
    """
    from django.conf import settings
    from django.utils import timezone
    from datetime import timedelta
    from modules.auth.accounts.models import UserTOTPDevice, BackupCode

    # Clean up unconfirmed TOTP devices
    unconfirmed_totp_retention_hours = getattr(settings, 'UNCONFIRMED_TOTP_RETENTION_HOURS', 24)
    totp_cutoff_time = timezone.now() - timedelta(hours=unconfirmed_totp_retention_hours)
    deleted_totp_count, _ = UserTOTPDevice.objects.filter(
        confirmed=False,
        created_at__lt=totp_cutoff_time
    ).delete()
    print(f"Cleaned up {deleted_totp_count} unconfirmed TOTP devices.")

    # Clean up used backup codes
    used_backup_code_retention_days = getattr(settings, 'USED_BACKUP_CODE_RETENTION_DAYS', 90)
    backup_code_cutoff_time = timezone.now() - timedelta(days=used_backup_code_retention_days)
    deleted_backup_count, _ = BackupCode.objects.filter(
        used=True,
        used_at__lt=backup_code_cutoff_time
    ).delete()
    print(f"Cleaned up {deleted_backup_count} used backup codes.")

    return f"MFA data cleanup complete. Deleted {deleted_totp_count} TOTP devices and {deleted_backup_count} backup codes."

@shared_task
def log_auth_event_task(user_id, event_type, ip_address, user_agent, device_info, success, details):
    """
    Celery task to log authentication events in the background.
    """
    from modules.auth.accounts.models import User, AuthAuditLog

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print(f"User with ID {user_id} not found for auth event logging.")
        return

    AuthAuditLog.objects.create(
        user=user,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        device_info=device_info,
        success=success,
        details=details or {}
    )
    print(f"Auth event logged for user {user.email}: {event_type} (Success: {success})")
