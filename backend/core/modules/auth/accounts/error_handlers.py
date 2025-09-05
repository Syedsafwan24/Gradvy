"""
Enhanced error handling utilities for better API responses and user experience.
"""
from rest_framework.response import Response
from rest_framework import status
from axes.helpers import get_lockout_response
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)

class ApiErrorHandler:
    """Enhanced error handling for API views"""
    
    @staticmethod
    def handle_validation_error(error, request=None):
        """Handle validation errors with user-friendly messages"""
        message = str(error)
        
        # Map common validation errors to user-friendly messages
        error_mappings = {
            'Invalid credentials': 'Invalid email or password.',
            'Account is disabled': 'Your account has been disabled. Please contact support.',
            'Account is temporarily locked': 'Account temporarily locked due to too many failed attempts. Please try again later.',
            'Invalid': 'Please check your input and try again.',
        }
        
        for key, value in error_mappings.items():
            if key.lower() in message.lower():
                message = value
                break
        
        return Response({
            'detail': message,
            'error_code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def handle_permission_denied(error, request=None):
        """Handle permission denied errors"""
        return Response({
            'detail': 'You do not have permission to perform this action.',
            'error_code': 'PERMISSION_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def handle_axes_lockout(request):
        """Handle django-axes lockout"""
        return Response({
            'detail': 'Account temporarily locked due to too many failed login attempts. Please try again later.',
            'error_code': 'ACCOUNT_LOCKED',
            'lockout': True
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    @staticmethod
    def handle_mfa_error(error_type, message=None):
        """Handle MFA-specific errors"""
        error_messages = {
            'invalid_code': 'Invalid authentication code. Please try again.',
            'expired_token': 'Authentication session expired. Please log in again.',
            'device_not_found': 'MFA device not found. Please contact support.',
            'already_enrolled': 'Multi-factor authentication is already enabled.',
            'not_enrolled': 'Multi-factor authentication is not enabled for this account.',
        }
        
        detail = message or error_messages.get(error_type, 'MFA verification failed.')
        
        return Response({
            'detail': detail,
            'error_code': f'MFA_{error_type.upper()}',
            'mfa_error': True
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def handle_rate_limit(request, retry_after=None):
        """Handle rate limiting errors"""
        detail = 'Too many requests. Please wait before trying again.'
        if retry_after:
            detail = f'Too many requests. Please wait {retry_after} seconds before trying again.'
            
        response_data = {
            'detail': detail,
            'error_code': 'RATE_LIMITED'
        }
        
        if retry_after:
            response_data['retry_after'] = retry_after
            
        return Response(response_data, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    @staticmethod
    def handle_server_error(error, request=None):
        """Handle internal server errors"""
        logger.error(f"Internal server error: {str(error)}", exc_info=True)
        
        return Response({
            'detail': 'An internal error occurred. Please try again later.',
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def check_lockout_status(request):
        """Check if request is currently locked out"""
        try:
            from axes.helpers import get_lockout_response
            return get_lockout_response(request) is not None
        except ImportError:
            # Axes not available
            return False
        except Exception as e:
            logger.warning(f"Error checking lockout status: {e}")
            return False

def with_error_handling(view_func):
    """Decorator to add comprehensive error handling to view methods"""
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ValidationError as e:
            request = args[1] if len(args) > 1 else kwargs.get('request')
            return ApiErrorHandler.handle_validation_error(e, request)
        except PermissionDenied as e:
            request = args[1] if len(args) > 1 else kwargs.get('request')
            return ApiErrorHandler.handle_permission_denied(e, request)
        except Exception as e:
            request = args[1] if len(args) > 1 else kwargs.get('request')
            return ApiErrorHandler.handle_server_error(e, request)
    
    return wrapper
