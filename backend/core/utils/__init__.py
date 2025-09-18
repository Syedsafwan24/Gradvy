"""
Core utilities package for Gradvy backend

This package contains shared utility modules for consistent API responses,
common functionality, and helper functions used across the application.
"""

# Make commonly used response classes easily importable
from .responses import (
    APISuccess,
    APIError,
    APIValidationError,
    AuthAPIResponse,
    PreferencesAPIResponse,
    StatusCodes,
    ErrorCodes,
    handle_exception,
    create_paginated_response,
    validate_required_fields
)

__all__ = [
    'APISuccess',
    'APIError',
    'APIValidationError',
    'AuthAPIResponse',
    'PreferencesAPIResponse',
    'StatusCodes',
    'ErrorCodes',
    'handle_exception',
    'create_paginated_response',
    'validate_required_fields'
]