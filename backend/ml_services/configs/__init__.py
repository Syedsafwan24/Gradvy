"""
backend/ml_services/configs/__init__.py
Configuration files and settings for ML services
Centralizes ML model configurations and service settings
RELEVANT FILES: core/settings.py, ML_Models/configs/, services/
"""

from .model_configs import MODEL_REGISTRY, get_model_config
from .service_configs import ML_SERVICE_SETTINGS

__all__ = [
    'MODEL_REGISTRY',
    'get_model_config', 
    'ML_SERVICE_SETTINGS'
]