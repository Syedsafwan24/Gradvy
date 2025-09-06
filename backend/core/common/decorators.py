"""
Reusable decorators for authentication and other common functionality.
"""

from functools import wraps
from typing import Callable, Any
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def handle_exceptions(view_func: Callable) -> Callable:
    """
    Decorator to add comprehensive error handling to view methods.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {view_func.__name__}: {str(e)}")
            return Response({
                'detail': 'Validation error occurred',
                'error_code': 'VALIDATION_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            logger.warning(f"Permission denied in {view_func.__name__}: {str(e)}")
            return Response({
                'detail': 'Permission denied',
                'error_code': 'PERMISSION_DENIED'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Unexpected error in {view_func.__name__}: {str(e)}", exc_info=True)
            return Response({
                'detail': 'An internal error occurred',
                'error_code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return wrapper


def require_mfa_enrollment(view_func: Callable) -> Callable:
    """
    Decorator to require MFA enrollment for view access.
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'detail': 'Authentication required',
                'error_code': 'AUTHENTICATION_REQUIRED'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not request.user.mfa_enrolled:
            return Response({
                'detail': 'MFA enrollment required',
                'error_code': 'MFA_ENROLLMENT_REQUIRED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(self, request, *args, **kwargs)
    
    return wrapper


def log_user_action(action_name: str = None):
    """
    Decorator to log user actions.
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            action = action_name or view_func.__name__
            user_info = f"User: {getattr(request.user, 'email', 'Anonymous')}"
            logger.info(f"Action: {action} - {user_info}")
            
            result = view_func(self, request, *args, **kwargs)
            
            # Log success/failure based on response status
            if hasattr(result, 'status_code'):
                if 200 <= result.status_code < 300:
                    logger.info(f"Action successful: {action} - {user_info}")
                else:
                    logger.warning(f"Action failed ({result.status_code}): {action} - {user_info}")
            
            return result
        
        return wrapper
    return decorator


def rate_limit_key_generator(group: str = 'default'):
    """
    Generate rate limit key for user actions.
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # This would integrate with a rate limiting system
            # For now, just pass through
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator