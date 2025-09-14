"""
backend/ml_services/base/service_interface.py
Abstract base class for high-level ML services
Defines interface for business logic ML services like learning path generation
RELEVANT FILES: base/model_interface.py, services/, core/apps/preferences/
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
import logging
from datetime import datetime
from dataclasses import dataclass

from .exceptions import MLServiceError, ValidationError, ConfigurationError
from .model_interface import BaseMLModel


@dataclass
class ServiceRequest:
    """Base class for service requests"""
    user_id: str
    request_id: str
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class ServiceResponse:
    """Base class for service responses"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseMLService(ABC):
    """
    Abstract base class for all ML services in the Gradvy platform.

    ML Services are high-level components that orchestrate one or more ML models
    to provide business functionality like learning path generation, question
    generation, or code evaluation.

    Key Design Principles:
    1. **Privacy First**: All user data is sanitized before model processing
    2. **Fault Tolerance**: Graceful degradation when models are unavailable
    3. **Caching**: Intelligent caching of results to reduce computation
    4. **Monitoring**: Comprehensive logging and metrics collection
    5. **Async Support**: Background processing for long-running operations

    Usage Example:
        service = LearningPathService()
        request = GenerateLearningPathRequest(
            user_id="123",
            learning_goals=["python", "web_development"],
            experience_level="beginner"
        )
        response = service.process(request)
    """

    def __init__(self, service_name: str, required_models: List[str] = None):
        """
        Initialize the ML service

        Args:
            service_name: Unique name for this service
            required_models: List of model names this service depends on
        """
        self.service_name = service_name
        self.required_models = required_models or []
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # Service state
        self._models: Dict[str, BaseMLModel] = {}
        self._is_initialized = False
        self._cache = {}  # Simple in-memory cache

        # Performance tracking
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._total_processing_time_ms = 0.0

    @property
    def is_initialized(self) -> bool:
        """Check if service is properly initialized"""
        return self._is_initialized

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the service and load required models.

        This method should:
        1. Load all required models
        2. Validate configuration
        3. Set up caching if needed
        4. Set _is_initialized = True

        Raises:
            ConfigurationError: If service configuration is invalid
            ModelLoadError: If required models fail to load
        """
        pass

    @abstractmethod
    def process(self, request: ServiceRequest) -> ServiceResponse:
        """
        Main processing method for the service.

        Args:
            request: Service-specific request object

        Returns:
            ServiceResponse with results or error information

        Raises:
            MLServiceError: If processing fails
            ValidationError: If request validation fails
        """
        pass

    @abstractmethod
    def validate_request(self, request: ServiceRequest) -> None:
        """
        Validate incoming service request.

        Args:
            request: Request to validate

        Raises:
            ValidationError: If validation fails
        """
        pass

    def add_model(self, model_name: str, model: BaseMLModel) -> None:
        """
        Add a model to this service.

        Args:
            model_name: Name to reference the model
            model: Model instance
        """
        self._models[model_name] = model
        self.logger.info(f"Added model {model_name} to service {self.service_name}")

    def get_model(self, model_name: str) -> BaseMLModel:
        """
        Get a model by name.

        Args:
            model_name: Name of the model

        Returns:
            Model instance

        Raises:
            KeyError: If model not found
        """
        if model_name not in self._models:
            raise KeyError(f"Model {model_name} not found in service {self.service_name}")
        return self._models[model_name]

    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities supported by this service.

        Returns:
            List of capability strings
        """
        capabilities = []
        for model in self._models.values():
            capabilities.extend(model.get_capabilities())
        return list(set(capabilities))  # Remove duplicates

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on the service.

        Returns:
            Dictionary with health status
        """
        try:
            if not self.is_initialized:
                return {
                    'service': self.service_name,
                    'status': 'uninitialized',
                    'healthy': False,
                    'message': 'Service not initialized'
                }

            # Check all models
            model_health = {}
            all_models_healthy = True

            for model_name, model in self._models.items():
                model_health[model_name] = model.health_check()
                if not model_health[model_name]['healthy']:
                    all_models_healthy = False

            return {
                'service': self.service_name,
                'status': 'healthy' if all_models_healthy else 'degraded',
                'healthy': all_models_healthy,
                'models': model_health,
                'stats': self.get_stats(),
                'last_check': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Health check failed for service {self.service_name}: {e}")
            return {
                'service': self.service_name,
                'status': 'unhealthy',
                'healthy': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get service performance statistics.

        Returns:
            Dictionary with service stats
        """
        success_rate = 0.0
        avg_processing_time = 0.0

        if self._total_requests > 0:
            success_rate = self._successful_requests / self._total_requests
            avg_processing_time = self._total_processing_time_ms / self._total_requests

        return {
            'service_name': self.service_name,
            'total_requests': self._total_requests,
            'successful_requests': self._successful_requests,
            'failed_requests': self._failed_requests,
            'success_rate': success_rate,
            'avg_processing_time_ms': avg_processing_time,
            'models_loaded': len([m for m in self._models.values() if m.is_loaded]),
            'total_models': len(self._models)
        }

    def _ensure_initialized(self) -> None:
        """Ensure service is initialized, initialize if necessary"""
        if not self.is_initialized:
            self.logger.info(f"Initializing service {self.service_name}")
            self.initialize()

    def _log_request(self, request: ServiceRequest, response: ServiceResponse) -> None:
        """Log request for monitoring and privacy compliance"""
        self._total_requests += 1
        self._total_processing_time_ms += response.processing_time_ms

        if response.success:
            self._successful_requests += 1
        else:
            self._failed_requests += 1

        # Log request (be careful with privacy)
        self.logger.info(
            f"Request processed - Service: {self.service_name}, "
            f"Success: {response.success}, "
            f"Time: {response.processing_time_ms:.2f}ms, "
            f"User: {request.user_id}"
        )

    def _cache_get(self, cache_key: str) -> Optional[Any]:
        """Get item from cache"""
        return self._cache.get(cache_key)

    def _cache_set(self, cache_key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set item in cache with TTL"""
        # Simple in-memory cache - in production, use Redis
        self._cache[cache_key] = {
            'value': value,
            'expires_at': datetime.now().timestamp() + ttl_seconds
        }

    def _cache_is_valid(self, cache_key: str) -> bool:
        """Check if cached item is still valid"""
        cached_item = self._cache.get(cache_key)
        if not cached_item:
            return False

        return datetime.now().timestamp() < cached_item['expires_at']

    def cleanup_cache(self) -> None:
        """Remove expired cache entries"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time >= item['expires_at']
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def __str__(self) -> str:
        status = "initialized" if self.is_initialized else "uninitialized"
        return f"{self.__class__.__name__}({self.service_name}, {status})"

    def __repr__(self) -> str:
        return self.__str__()