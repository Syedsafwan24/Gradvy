"""
backend/ml_services/base/__init__.py
Base classes and interfaces for ML services
Provides abstract base classes for consistent ML service architecture
RELEVANT FILES: ml_services/__init__.py, ml_services/models/, ml_services/services/
"""

from .exceptions import MLServiceError, ModelLoadError, InferenceError
from .model_interface import BaseMLModel
from .service_interface import BaseMLService

__all__ = [
    'MLServiceError',
    'ModelLoadError',
    'InferenceError',
    'BaseMLModel',
    'BaseMLService'
]