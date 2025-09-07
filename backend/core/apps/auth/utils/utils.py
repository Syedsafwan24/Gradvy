import secrets
import string
import logging
from ..models import BackupCode

logger = logging.getLogger(__name__)

def log_auth_event(user, event_type, request, success=True, details=None):
    """No-op function - audit logging has been removed for clean authentication."""
    pass

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
