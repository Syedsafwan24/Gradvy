"""
Custom exceptions for authentication module.
"""

from rest_framework import status
from rest_framework.response import Response
from .constants import ErrorCodes, Messages


class AuthenticationException(Exception):
    """Base exception for authentication errors."""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.error_code = error_code or ErrorCodes.VALIDATION_ERROR
        self.status_code = status_code
        super().__init__(message)
    
    def to_response(self) -> Response:
        """Convert exception to HTTP response."""
        return Response({
            'detail': self.message,
            'error_code': self.error_code
        }, status=self.status_code)


class InvalidCredentialsError(AuthenticationException):
    """Exception for invalid login credentials."""
    
    def __init__(self):
        super().__init__(
            Messages.INVALID_CREDENTIALS,
            ErrorCodes.INVALID_CREDENTIALS,
            status.HTTP_401_UNAUTHORIZED
        )


class AccountLockedException(AuthenticationException):
    """Exception for locked user accounts."""
    
    def __init__(self):
        super().__init__(
            Messages.ACCOUNT_LOCKED,
            ErrorCodes.ACCOUNT_LOCKED,
            status.HTTP_429_TOO_MANY_REQUESTS
        )


class MFARequiredException(AuthenticationException):
    """Exception when MFA verification is required."""
    
    def __init__(self):
        super().__init__(
            Messages.MFA_REQUIRED,
            ErrorCodes.MFA_REQUIRED,
            status.HTTP_200_OK  # Not an error, but requires additional step
        )


class MFAInvalidCodeError(AuthenticationException):
    """Exception for invalid MFA codes."""
    
    def __init__(self):
        super().__init__(
            Messages.MFA_INVALID_CODE,
            ErrorCodes.MFA_INVALID_CODE,
            status.HTTP_400_BAD_REQUEST
        )


class MFAExpiredTokenError(AuthenticationException):
    """Exception for expired MFA tokens."""
    
    def __init__(self):
        super().__init__(
            Messages.MFA_EXPIRED_TOKEN,
            ErrorCodes.MFA_EXPIRED_TOKEN,
            status.HTTP_400_BAD_REQUEST
        )


class MFADeviceNotFoundError(AuthenticationException):
    """Exception when MFA device is not found."""
    
    def __init__(self):
        super().__init__(
            Messages.MFA_DEVICE_NOT_FOUND,
            ErrorCodes.MFA_DEVICE_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST
        )


class MFAAlreadyEnrolledException(AuthenticationException):
    """Exception when user is already enrolled in MFA."""
    
    def __init__(self):
        super().__init__(
            Messages.MFA_ALREADY_ENROLLED,
            ErrorCodes.MFA_ALREADY_ENROLLED,
            status.HTTP_400_BAD_REQUEST
        )


class MFANotEnrolledException(AuthenticationException):
    """Exception when user is not enrolled in MFA."""
    
    def __init__(self):
        super().__init__(
            Messages.MFA_NOT_ENROLLED,
            ErrorCodes.MFA_NOT_ENROLLED,
            status.HTTP_400_BAD_REQUEST
        )