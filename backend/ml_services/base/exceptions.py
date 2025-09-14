"""
backend/ml_services/base/exceptions.py
Custom exceptions for ML services with detailed error handling
Provides specific exception types for different ML operation failures
RELEVANT FILES: base/model_interface.py, base/service_interface.py, services/
"""

class MLServiceError(Exception):
    """Base exception for all ML service errors"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        Initialize ML service error with detailed information

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for handling
            details: Additional error context and debugging information
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self):
        """Convert exception to dictionary for JSON serialization"""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }


class ModelLoadError(MLServiceError):
    """Raised when a model fails to load"""

    def __init__(self, model_name: str, reason: str, details: dict = None):
        message = f"Failed to load model '{model_name}': {reason}"
        super().__init__(
            message=message,
            error_code="MODEL_LOAD_FAILED",
            details={
                'model_name': model_name,
                'reason': reason,
                **(details or {})
            }
        )


class InferenceError(MLServiceError):
    """Raised when model inference fails"""

    def __init__(self, model_name: str, input_data: str, reason: str, details: dict = None):
        message = f"Inference failed for model '{model_name}': {reason}"
        super().__init__(
            message=message,
            error_code="INFERENCE_FAILED",
            details={
                'model_name': model_name,
                'input_preview': input_data[:100] + "..." if len(input_data) > 100 else input_data,
                'reason': reason,
                **(details or {})
            }
        )


class ModelNotFoundError(MLServiceError):
    """Raised when a requested model is not available"""

    def __init__(self, model_name: str, available_models: list = None):
        message = f"Model '{model_name}' not found"
        if available_models:
            message += f". Available models: {', '.join(available_models)}"

        super().__init__(
            message=message,
            error_code="MODEL_NOT_FOUND",
            details={
                'requested_model': model_name,
                'available_models': available_models or []
            }
        )


class ResourceExhaustedError(MLServiceError):
    """Raised when system resources are insufficient for ML operations"""

    def __init__(self, resource_type: str, required: str, available: str, details: dict = None):
        message = f"Insufficient {resource_type}: required {required}, available {available}"
        super().__init__(
            message=message,
            error_code="RESOURCE_EXHAUSTED",
            details={
                'resource_type': resource_type,
                'required': required,
                'available': available,
                **(details or {})
            }
        )


class ValidationError(MLServiceError):
    """Raised when input validation fails"""

    def __init__(self, field: str, value: str, reason: str, details: dict = None):
        message = f"Validation failed for field '{field}': {reason}"
        super().__init__(
            message=message,
            error_code="VALIDATION_FAILED",
            details={
                'field': field,
                'value': str(value)[:100],  # Truncate for security
                'reason': reason,
                **(details or {})
            }
        )


class ConfigurationError(MLServiceError):
    """Raised when ML service configuration is invalid"""

    def __init__(self, config_key: str, reason: str, details: dict = None):
        message = f"Configuration error for '{config_key}': {reason}"
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={
                'config_key': config_key,
                'reason': reason,
                **(details or {})
            }
        )