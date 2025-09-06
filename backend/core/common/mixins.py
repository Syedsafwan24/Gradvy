"""
Reusable mixins for views and other components.
"""

from typing import Dict, Any
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging


logger = logging.getLogger(__name__)


class StandardResponseMixin:
    """Mixin to standardize API response formats."""
    
    def success_response(self, data: Any = None, message: str = None, status_code: int = status.HTTP_200_OK) -> Response:
        """Create standardized success response."""
        response_data = {}
        
        if data is not None:
            response_data.update(data if isinstance(data, dict) else {'data': data})
        
        if message:
            response_data['message'] = message
            
        return Response(response_data, status=status_code)
    
    def error_response(self, message: str, error_code: str = None, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
        """Create standardized error response."""
        response_data = {'detail': message}
        
        if error_code:
            response_data['error_code'] = error_code
            
        return Response(response_data, status=status_code)


class LoggingMixin:
    """Mixin to add request/response logging."""
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to add logging."""
        logger.info(f"{request.method} {request.path} - User: {getattr(request.user, 'email', 'Anonymous')}")
        
        try:
            response = super().dispatch(request, *args, **kwargs)
            logger.info(f"Response {response.status_code} for {request.method} {request.path}")
            return response
        except Exception as e:
            logger.error(f"Error in {request.method} {request.path}: {str(e)}")
            raise


class CSRFExemptMixin:
    """Mixin to exempt views from CSRF protection."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AuthenticationRequiredMixin:
    """Mixin to ensure user is authenticated with better error handling."""
    
    def dispatch(self, request, *args, **kwargs):
        """Check authentication before processing request."""
        if not request.user.is_authenticated:
            return Response({
                'detail': 'Authentication required',
                'error_code': 'AUTHENTICATION_REQUIRED'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return super().dispatch(request, *args, **kwargs)


class IPAddressMixin:
    """Mixin to easily get client IP address."""
    
    def get_client_ip(self, request) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        
        return ip