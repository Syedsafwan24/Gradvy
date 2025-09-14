"""
backend/ml_services/__init__.py
AI-powered learning system ML services module
Provides machine learning capabilities for personalized learning paths
RELEVANT FILES: core/settings.py, core/apps/preferences/models.py, requirements.txt, ML_Models/configs/
"""

from .base.exceptions import MLServiceError, ModelLoadError, InferenceError
from .base.model_interface import BaseMLModel
from .base.service_interface import BaseMLService

__version__ = "1.0.0"
__author__ = "Gradvy ML Team"

# ML Service Registry - will be populated by individual services
ML_SERVICES = {}

def register_service(name: str, service_class):
    """Register an ML service for use throughout the application"""
    ML_SERVICES[name] = service_class

def get_service(name: str):
    """Get a registered ML service by name"""
    if name not in ML_SERVICES:
        raise ValueError(f"ML service '{name}' not found. Available services: {list(ML_SERVICES.keys())}")
    return ML_SERVICES[name]

# Import core services to trigger registration
try:
    from .services.learning_path_service import LearningPathService
    from .services.question_generator_service import QuestionGeneratorService
    from .services.code_evaluator_service import CodeEvaluatorService
except ImportError:
    # Services not yet implemented, will be added progressively
    pass