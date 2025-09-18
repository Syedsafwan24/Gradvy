"""
Standard API Response Utilities for Gradvy Backend

This module provides standardized response classes and utilities for consistent API responses
across all endpoints. All API views should use these utilities to ensure consistent response
formats, proper error handling, and professional API responses.

RELEVANT FILES: apps/auth/api/views.py, apps/preferences/views.py, frontend/src/utils/apiErrors.js
"""

from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
import uuid
import logging

logger = logging.getLogger(__name__)

# Standard HTTP Status Codes
class StatusCodes:
    """Standard HTTP status codes for consistent usage"""
    # Success codes
    OK = status.HTTP_200_OK
    CREATED = status.HTTP_201_CREATED
    ACCEPTED = status.HTTP_202_ACCEPTED
    NO_CONTENT = status.HTTP_204_NO_CONTENT

    # Client error codes
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
    FORBIDDEN = status.HTTP_403_FORBIDDEN
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    METHOD_NOT_ALLOWED = status.HTTP_405_METHOD_NOT_ALLOWED
    CONFLICT = status.HTTP_409_CONFLICT
    UNPROCESSABLE_ENTITY = status.HTTP_422_UNPROCESSABLE_ENTITY
    TOO_MANY_REQUESTS = status.HTTP_429_TOO_MANY_REQUESTS

    # Server error codes
    INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    BAD_GATEWAY = status.HTTP_502_BAD_GATEWAY
    SERVICE_UNAVAILABLE = status.HTTP_503_SERVICE_UNAVAILABLE


# Standard Error Codes
class ErrorCodes:
    """Standard error codes for consistent error classification"""
    # Authentication & Authorization
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    MFA_REQUIRED = "MFA_REQUIRED"
    INVALID_MFA_CODE = "INVALID_MFA_CODE"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_INPUT_FORMAT = "INVALID_INPUT_FORMAT"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"

    # Business Logic
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # System
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


class StandardAPIResponse:
    """Base class for standardized API responses"""

    @staticmethod
    def _generate_meta(request_id=None):
        """Generate metadata for API responses"""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id or str(uuid.uuid4())[:8]
        }

    @staticmethod
    def _sanitize_data(data):
        """Sanitize data to ensure JSON serialization"""
        if data is None:
            return None
        # Add any necessary data sanitization here
        return data


class APISuccess(StandardAPIResponse):
    """Standardized success response class"""

    @classmethod
    def create(cls, data=None, message="Operation completed successfully",
               status_code=StatusCodes.OK, meta=None, **kwargs):
        """
        Create a standardized success response

        Args:
            data: Response data payload
            message: Success message for the user
            status_code: HTTP status code (default: 200)
            meta: Additional metadata
            **kwargs: Additional fields to include in response

        Returns:
            Response: DRF Response object with standardized format
        """
        response_data = {
            "success": True,
            "message": message,
            "data": cls._sanitize_data(data),
            "meta": meta or cls._generate_meta()
        }

        # Add any additional fields
        response_data.update(kwargs)

        return Response(response_data, status=status_code)

    @classmethod
    def created(cls, data=None, message="Resource created successfully", **kwargs):
        """Create a 201 Created response"""
        return cls.create(data=data, message=message, status_code=StatusCodes.CREATED, **kwargs)

    @classmethod
    def accepted(cls, data=None, message="Request accepted for processing", **kwargs):
        """Create a 202 Accepted response"""
        return cls.create(data=data, message=message, status_code=StatusCodes.ACCEPTED, **kwargs)

    @classmethod
    def no_content(cls, message="Operation completed successfully"):
        """Create a 204 No Content response"""
        response_data = {
            "success": True,
            "message": message,
            "meta": cls._generate_meta()
        }
        return Response(response_data, status=StatusCodes.NO_CONTENT)


class APIError(StandardAPIResponse):
    """Standardized error response class"""

    @classmethod
    def create(cls, message="An error occurred", code=None, details=None,
               field_errors=None, status_code=StatusCodes.BAD_REQUEST,
               meta=None, **kwargs):
        """
        Create a standardized error response

        Args:
            message: User-friendly error message
            code: Error code for client handling
            details: Additional error details
            field_errors: Field-specific validation errors
            status_code: HTTP status code
            meta: Additional metadata
            **kwargs: Additional fields to include in error object

        Returns:
            Response: DRF Response object with standardized error format
        """
        error_data = {
            "code": code,
            "message": message,
            "details": details,
            "field_errors": field_errors or {}
        }

        # Add any additional error fields
        error_data.update(kwargs)

        response_data = {
            "success": False,
            "error": error_data,
            "meta": meta or cls._generate_meta()
        }

        # Log error for debugging (exclude sensitive data)
        logger.warning(f"API Error: {code or 'UNKNOWN'} - {message}")

        return Response(response_data, status=status_code)

    @classmethod
    def bad_request(cls, message="Invalid request", code=ErrorCodes.VALIDATION_ERROR, **kwargs):
        """Create a 400 Bad Request response"""
        return cls.create(message=message, code=code, status_code=StatusCodes.BAD_REQUEST, **kwargs)

    @classmethod
    def unauthorized(cls, message="Authentication required", code=ErrorCodes.INVALID_CREDENTIALS, **kwargs):
        """Create a 401 Unauthorized response"""
        return cls.create(message=message, code=code, status_code=StatusCodes.UNAUTHORIZED, **kwargs)

    @classmethod
    def forbidden(cls, message="Access denied", code=ErrorCodes.INSUFFICIENT_PERMISSIONS, **kwargs):
        """Create a 403 Forbidden response"""
        return cls.create(message=message, code=code, status_code=StatusCodes.FORBIDDEN, **kwargs)

    @classmethod
    def not_found(cls, message="Resource not found", code=ErrorCodes.RESOURCE_NOT_FOUND, **kwargs):
        """Create a 404 Not Found response"""
        return cls.create(message=message, code=code, status_code=StatusCodes.NOT_FOUND, **kwargs)

    @classmethod
    def conflict(cls, message="Resource conflict", code=ErrorCodes.RESOURCE_CONFLICT, **kwargs):
        """Create a 409 Conflict response"""
        return cls.create(message=message, code=code, status_code=StatusCodes.CONFLICT, **kwargs)

    @classmethod
    def too_many_requests(cls, message="Rate limit exceeded", code=ErrorCodes.RATE_LIMIT_EXCEEDED, **kwargs):
        """Create a 429 Too Many Requests response"""
        return cls.create(message=message, code=code, status_code=StatusCodes.TOO_MANY_REQUESTS, **kwargs)

    @classmethod
    def internal_server_error(cls, message="Internal server error", code=ErrorCodes.INTERNAL_ERROR, **kwargs):
        """Create a 500 Internal Server Error response"""
        return cls.create(message=message, code=code, status_code=StatusCodes.INTERNAL_SERVER_ERROR, **kwargs)


class APIValidationError(APIError):
    """Specialized class for validation errors"""

    @classmethod
    def create_from_serializer(cls, serializer):
        """
        Create validation error response from DRF serializer errors

        Args:
            serializer: DRF serializer with validation errors

        Returns:
            Response: Standardized validation error response
        """
        field_errors = {}
        general_errors = []

        for field, errors in serializer.errors.items():
            if field == 'non_field_errors':
                general_errors.extend(errors)
            else:
                # Convert error messages to strings
                field_errors[field] = [str(error) for error in errors]

        # Use first general error as main message, or default message
        if general_errors:
            message = str(general_errors[0])
        elif field_errors:
            # Use first field error as main message
            first_field = next(iter(field_errors))
            message = f"Validation error in {first_field}: {field_errors[first_field][0]}"
        else:
            message = "Validation failed"

        return cls.create(
            message=message,
            code=ErrorCodes.VALIDATION_ERROR,
            field_errors=field_errors,
            details={"general_errors": general_errors} if general_errors else None,
            status_code=StatusCodes.BAD_REQUEST
        )

    @classmethod
    def required_field(cls, field_name):
        """Create error for missing required field"""
        return cls.create(
            message=f"'{field_name}' is required",
            code=ErrorCodes.REQUIRED_FIELD_MISSING,
            field_errors={field_name: ["This field is required"]},
            status_code=StatusCodes.BAD_REQUEST
        )

    @classmethod
    def invalid_format(cls, field_name, expected_format):
        """Create error for invalid field format"""
        return cls.create(
            message=f"Invalid format for '{field_name}'. Expected: {expected_format}",
            code=ErrorCodes.INVALID_INPUT_FORMAT,
            field_errors={field_name: [f"Invalid format. Expected: {expected_format}"]},
            status_code=StatusCodes.BAD_REQUEST
        )


class AuthAPIResponse:
    """Specialized response utilities for authentication endpoints"""

    @staticmethod
    def login_success(user_data, tokens, message="Login successful"):
        """Create successful login response"""
        return APISuccess.create(
            data={
                "user": user_data,
                "access_token": tokens.get("access"),
                "refresh_token": tokens.get("refresh")
            },
            message=message
        )

    @staticmethod
    def mfa_required(mfa_token, message="Multi-factor authentication required"):
        """Create MFA required response"""
        return APISuccess.create(
            data={"mfa_token": mfa_token, "mfa_required": True},
            message=message,
            status_code=StatusCodes.ACCEPTED  # 202 indicates further action needed
        )

    @staticmethod
    def invalid_credentials():
        """Create invalid credentials error"""
        return APIError.unauthorized(
            message="Invalid email or password",
            code=ErrorCodes.INVALID_CREDENTIALS
        )

    @staticmethod
    def account_locked():
        """Create account locked error"""
        return APIError.too_many_requests(
            message="Account temporarily locked due to too many failed login attempts",
            code=ErrorCodes.ACCOUNT_LOCKED
        )

    @staticmethod
    def invalid_mfa_code():
        """Create invalid MFA code error"""
        return APIError.bad_request(
            message="Invalid or expired MFA code",
            code=ErrorCodes.INVALID_MFA_CODE
        )

    @staticmethod
    def token_expired():
        """Create token expired error"""
        return APIError.unauthorized(
            message="Token has expired. Please login again",
            code=ErrorCodes.TOKEN_EXPIRED
        )


class PreferencesAPIResponse:
    """Specialized response utilities for preferences endpoints"""

    @staticmethod
    def preferences_retrieved(preferences_data, message="Preferences retrieved successfully"):
        """Create successful preferences retrieval response"""
        return APISuccess.create(
            data=preferences_data,
            message=message
        )

    @staticmethod
    def preferences_updated(preferences_data, message="Preferences updated successfully"):
        """Create successful preferences update response"""
        return APISuccess.create(
            data=preferences_data,
            message=message
        )

    @staticmethod
    def onboarding_completed(preferences_data, completion_percentage, message="Onboarding completed successfully"):
        """Create successful onboarding completion response"""
        return APISuccess.created(
            data=preferences_data,
            message=message,
            completion_percentage=completion_percentage
        )

    @staticmethod
    def preferences_not_found():
        """Create preferences not found error"""
        return APIError.not_found(
            message="User preferences not found. Please complete onboarding first",
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            details={"onboarding_required": True}
        )

    @staticmethod
    def mongodb_validation_error(mongodb_error):
        """Create MongoDB validation error response"""
        # Parse MongoDB error for user-friendly message
        error_message = "Invalid data provided. Please check your selections"

        # Extract specific validation issues from MongoDB error if possible
        if "ValidationError" in str(mongodb_error):
            error_message = "Some of your selections contain invalid values. Please review your choices"

        return APIError.bad_request(
            message=error_message,
            code=ErrorCodes.VALIDATION_ERROR,
            details={"mongodb_error": str(mongodb_error)}
        )


# Utility functions for common operations
def handle_exception(exception, default_message="An unexpected error occurred",
                    status_code=StatusCodes.INTERNAL_SERVER_ERROR):
    """
    Handle unexpected exceptions with standardized error response

    Args:
        exception: The caught exception
        default_message: Default error message for user
        status_code: HTTP status code to return

    Returns:
        Response: Standardized error response
    """
    logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)

    return APIError.create(
        message=default_message,
        code=ErrorCodes.INTERNAL_ERROR,
        details={"exception_type": type(exception).__name__} if hasattr(exception, '__name__') else None,
        status_code=status_code
    )


def create_paginated_response(data, page_info, message="Data retrieved successfully"):
    """
    Create standardized paginated response

    Args:
        data: List of data items
        page_info: Pagination information (page, total_pages, total_items, etc.)
        message: Success message

    Returns:
        Response: Standardized paginated response
    """
    return APISuccess.create(
        data=data,
        message=message,
        pagination=page_info
    )


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in data

    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names

    Returns:
        APIError response if validation fails, None if validation passes
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)

    if missing_fields:
        field_errors = {field: ["This field is required"] for field in missing_fields}
        return APIValidationError.create(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            code=ErrorCodes.REQUIRED_FIELD_MISSING,
            field_errors=field_errors
        )

    return None