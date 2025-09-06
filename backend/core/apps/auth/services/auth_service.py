"""
Authentication service layer.

Handles core authentication operations including login, logout,
token management, and authentication validation.
"""

from typing import Dict, Optional, Tuple
import jwt
import logging
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from axes.exceptions import AxesBackendPermissionDenied

logger = logging.getLogger(__name__)
User = get_user_model()


class AuthenticationService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def generate_tokens(user) -> Dict[str, str]:
        """Generate JWT access and refresh tokens for a user."""
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        return {
            'access': str(access),
            'refresh': str(refresh),
        }
    
    @staticmethod
    def generate_mfa_token(user) -> str:
        """Generate temporary MFA token for two-step authentication."""
        mfa_payload = {
            'user_id': user.id,
            'mfa_pending': True,
            'exp': timezone.now().timestamp() + 300,  # 5 minutes expiry
            'iat': timezone.now().timestamp(),
        }
        return jwt.encode(mfa_payload, settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_mfa_token(token: str) -> Optional[Dict]:
        """Verify and decode MFA token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            if not payload.get('mfa_pending'):
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("MFA token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid MFA token")
            return None
    
    @staticmethod
    def validate_user_credentials(user) -> Tuple[bool, str]:
        """
        Validate user credentials and account status.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not user.is_active:
            return False, "Account is disabled"
        
        if user.is_locked:
            return False, "Account is temporarily locked"
        
        return True, ""
    
    @staticmethod
    def blacklist_refresh_token(refresh_token: str) -> bool:
        """Blacklist a refresh token (logout)."""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False