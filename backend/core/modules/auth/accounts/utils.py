import secrets
import string
import logging
from django.utils import timezone
from .models import AuthAuditLog, BackupCode
from .tasks import log_auth_event_task # Import the new Celery task

logger = logging.getLogger(__name__)

def log_auth_event(user, event_type, request, success=True, details=None):
    """Log authentication events for audit purposes asynchronously."""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Basic device info
    device_info = {
        'user_agent': user_agent,
        'method': request.method,
        'path': request.path,
    }
    
    # Add any additional details
    if details:
        device_info.update(details)
    
    # Try to call the Celery task, but fallback to direct logging if Celery is not available
    try:
        log_auth_event_task.delay(
            user.id, # Pass user ID instead of user object
            event_type,
            ip_address,
            user_agent,
            device_info,
            success,
            details or {}
        )
    except Exception as e:
        logger.warning(f"Celery task failed, logging auth event directly: {e}")
        # Fallback to direct database logging
        try:
            AuthAuditLog.objects.create(
                user=user,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                device_info=device_info,
                success=success,
                details=details or {}
            )
        except Exception as db_error:
            logger.error(f"Failed to log auth event both via Celery and directly: {db_error}")

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_backup_codes(user, count=10):
    """Generate backup codes for MFA fallback"""
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        BackupCode.objects.create(user=user, code=code)
        codes.append(code)
    return codes

def revoke_user_sessions(user):
    """Revoke all active sessions for a user"""
    # This would invalidate JWT refresh tokens and clear sessions
    # Implementation depends on your session/JWT storage strategy
    pass
