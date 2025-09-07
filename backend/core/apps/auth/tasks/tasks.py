from celery import shared_task

@shared_task
def send_welcome_email(user_email):
    """
    Send welcome email to new user.
    TODO: Implement actual email sending logic.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Sending welcome email to {user_email}")
    # TODO: Replace with actual email service implementation
    # Example: send_email_service.send(to=user_email, template='welcome')
    
    return f"Welcome email queued for {user_email}"

@shared_task
def process_user_data(user_id):
    """
    Process user data in the background.
    TODO: Implement actual data processing logic.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Processing user data for user ID: {user_id}")
    # TODO: Replace with actual data processing logic
    
    return f"User data processed for ID: {user_id}"

@shared_task
def cleanup_user_mfa_data(user_id):
    """
    Clean up all MFA-related data for a specific user when MFA is disabled.
    This includes backup codes, unconfirmed TOTP devices, and other MFA artifacts.
    """
    import logging
    from django.contrib.auth import get_user_model
    from django_otp.plugins.otp_totp.models import TOTPDevice
    from ..models import BackupCode

    logger = logging.getLogger(__name__)
    User = get_user_model()
    print("here in the task ")
    try:
        user = User.objects.get(id=user_id)
        
        # Delete all backup codes (used and unused) for this user
        backup_codes_deleted, _ = BackupCode.objects.filter(user=user).delete()
        
        # Delete any remaining unconfirmed TOTP devices for this user
        unconfirmed_totp_deleted, _ = TOTPDevice.objects.filter(
            user=user, 
            confirmed=False
        ).delete()
        
        logger.info(
            f"MFA cleanup completed for user {user.email}: "
            f"Deleted {backup_codes_deleted} backup codes, "
            f"{unconfirmed_totp_deleted} unconfirmed TOTP devices"
        )
        
        return f"MFA cleanup completed for user {user_id}: {backup_codes_deleted} backup codes, {unconfirmed_totp_deleted} TOTP devices deleted"
        
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found during MFA cleanup")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Error during MFA cleanup for user {user_id}: {str(e)}")
        return f"Error during MFA cleanup for user {user_id}: {str(e)}"

@shared_task
def clean_mfa_data():
    """
    Cleans up old unconfirmed TOTP devices and used backup codes.
    """
    import logging
    from django.conf import settings
    from django.utils import timezone
    from datetime import timedelta
    from django_otp.plugins.otp_totp.models import TOTPDevice
    from ..models import BackupCode

    logger = logging.getLogger(__name__)

    # Clean up unconfirmed TOTP devices
    unconfirmed_totp_retention_hours = getattr(settings, 'UNCONFIRMED_TOTP_RETENTION_HOURS', 24)
    totp_cutoff_time = timezone.now() - timedelta(hours=unconfirmed_totp_retention_hours)
    deleted_totp_count, _ = TOTPDevice.objects.filter(
        confirmed=False,
        created_at__lt=totp_cutoff_time
    ).delete()
    logger.info(f"Cleaned up {deleted_totp_count} unconfirmed TOTP devices")

    # Clean up used backup codes
    used_backup_code_retention_days = getattr(settings, 'USED_BACKUP_CODE_RETENTION_DAYS', 90)
    backup_code_cutoff_time = timezone.now() - timedelta(days=used_backup_code_retention_days)
    deleted_backup_count, _ = BackupCode.objects.filter(
        used=True,
        used_at__lt=backup_code_cutoff_time
    ).delete()
    logger.info(f"Cleaned up {deleted_backup_count} used backup codes")

    return f"MFA data cleanup complete. Deleted {deleted_totp_count} TOTP devices and {deleted_backup_count} backup codes."

