"""
backend/ml_services/utils/model_registry.py
Central registry for managing all ML models in the system
Handles model loading, unloading, resource management, and health monitoring
RELEVANT FILES: configs/model_configs.py, base/model_interface.py, base/exceptions.py
"""

import threading
import time
import logging
import psutil
import gc
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from ..base.model_interface import BaseMLModel, ModelMetadata
from ..base.exceptions import (
    ModelLoadError, ModelNotFoundError, ResourceExhaustedError,
    ConfigurationError
)
from ..configs.model_configs import (
    MODEL_REGISTRY as MODEL_CONFIG_REGISTRY,
    get_model_config,
    get_deployment_profile
)


@dataclass
class ResourceUsage:
    """Current system resource usage"""
    memory_used_gb: float
    memory_available_gb: float
    memory_percent: float
    cpu_percent: float
    gpu_memory_used_gb: float = 0.0
    gpu_memory_available_gb: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ModelStatus:
    """Status information for a model"""
    name: str
    is_loaded: bool
    load_time: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    memory_usage_gb: float
    health_status: str  # 'healthy', 'degraded', 'unhealthy', 'unknown'
    error_count: int = 0


class ModelRegistry:
    """
    Central registry for managing ML models.

    This class is responsible for:
    1. Loading and unloading models based on demand
    2. Monitoring system resources and preventing overload
    3. Providing health checks and performance monitoring
    4. Managing model lifecycle and cleanup
    5. Implementing intelligent caching and eviction policies

    Thread-safe design for concurrent access.
    """

    def __init__(self, deployment_profile: str = "development"):
        """
        Initialize the model registry.

        Args:
            deployment_profile: Deployment profile to use ('development', 'production_small', 'production_large')
        """
        self.deployment_profile = deployment_profile
        self.profile_config = get_deployment_profile(deployment_profile)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # Model storage
        self._models: Dict[str, BaseMLModel] = {}
        self._model_classes: Dict[str, Type[BaseMLModel]] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety

        # Resource monitoring
        self._resource_usage: Optional[ResourceUsage] = None
        self._resource_monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()

        # Usage tracking
        self._model_usage: Dict[str, ModelStatus] = {}
        self._load_queue: List[str] = []  # Models queued for loading
        self._unload_candidates: List[str] = []  # Models candidates for unloading

        # Configuration
        self.max_memory_gb = self.profile_config.get("max_memory_gb", 16)
        self.allow_cpu_only = self.profile_config.get("allow_cpu_only", True)
        self.quantization_aggressive = self.profile_config.get("quantization_aggressive", True)

        # Start resource monitoring
        self._start_resource_monitoring()

        self.logger.info(f"ModelRegistry initialized with profile: {deployment_profile}")

    def register_model_class(self, model_name: str, model_class: Type[BaseMLModel]) -> None:
        """
        Register a model class for lazy loading.

        Args:
            model_name: Name of the model
            model_class: Model class to instantiate
        """
        with self._lock:
            if model_name not in MODEL_CONFIG_REGISTRY:
                raise ConfigurationError(
                    model_name,
                    f"Model '{model_name}' not found in configuration registry"
                )

            self._model_classes[model_name] = model_class
            self._model_usage[model_name] = ModelStatus(
                name=model_name,
                is_loaded=False,
                load_time=None,
                last_used=None,
                usage_count=0,
                memory_usage_gb=0.0,
                health_status='unknown'
            )

        self.logger.info(f"Registered model class: {model_name}")

    def get_model(self, model_name: str, load_if_needed: bool = True) -> BaseMLModel:
        """
        Get a model by name, loading it if necessary.

        Args:
            model_name: Name of the model
            load_if_needed: Whether to load the model if not already loaded

        Returns:
            The requested model instance

        Raises:
            ModelNotFoundError: If model is not registered
            ModelLoadError: If model loading fails
            ResourceExhaustedError: If insufficient resources
        """
        with self._lock:
            # Check if model is registered
            if model_name not in self._model_classes:
                available_models = list(self._model_classes.keys())
                raise ModelNotFoundError(model_name, available_models)

            # Check if model is already loaded
            if model_name in self._models:
                self._update_model_usage(model_name)
                return self._models[model_name]

            # Load model if requested
            if load_if_needed:
                self._load_model(model_name)
                self._update_model_usage(model_name)
                return self._models[model_name]
            else:
                raise ModelNotFoundError(
                    model_name,
                    list(self._models.keys())  # Currently loaded models
                )

    def _load_model(self, model_name: str) -> None:
        """
        Load a model into memory.

        Args:
            model_name: Name of the model to load

        Raises:
            ModelLoadError: If loading fails
            ResourceExhaustedError: If insufficient resources
        """
        config = get_model_config(model_name)
        model_class = self._model_classes[model_name]

        # Check resource availability
        self._check_resource_availability(model_name)

        # Potentially unload other models to make space
        self._manage_memory_pressure(config['memory_requirement_gb'])

        try:
            self.logger.info(f"Loading model: {model_name}")
            start_time = time.time()

            # Create and load model
            model = model_class(model_name, config)
            model.load()

            load_time = time.time() - start_time

            # Store model and update tracking
            self._models[model_name] = model
            self._model_usage[model_name].is_loaded = True
            self._model_usage[model_name].load_time = datetime.now()
            self._model_usage[model_name].memory_usage_gb = config['memory_requirement_gb']

            self.logger.info(
                f"Model {model_name} loaded successfully in {load_time:.2f}s, "
                f"Memory: {config['memory_requirement_gb']:.1f}GB"
            )

        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            self._model_usage[model_name].error_count += 1
            self._model_usage[model_name].health_status = 'unhealthy'
            raise ModelLoadError(model_name, str(e))

    def _unload_model(self, model_name: str) -> None:
        """
        Unload a model from memory.

        Args:
            model_name: Name of the model to unload
        """
        with self._lock:
            if model_name not in self._models:
                self.logger.warning(f"Attempted to unload non-loaded model: {model_name}")
                return

            try:
                self.logger.info(f"Unloading model: {model_name}")

                # Unload the model
                self._models[model_name].unload()

                # Remove from tracking
                del self._models[model_name]
                self._model_usage[model_name].is_loaded = False
                self._model_usage[model_name].memory_usage_gb = 0.0

                # Force garbage collection
                gc.collect()

                self.logger.info(f"Model {model_name} unloaded successfully")

            except Exception as e:
                self.logger.error(f"Error unloading model {model_name}: {e}")

    def _check_resource_availability(self, model_name: str) -> None:
        """
        Check if sufficient resources are available to load the model.

        Args:
            model_name: Name of the model to check

        Raises:
            ResourceExhaustedError: If insufficient resources
        """
        config = get_model_config(model_name)
        required_memory = config['memory_requirement_gb']

        # Get current resource usage
        self._update_resource_usage()

        if self._resource_usage.memory_available_gb < required_memory:
            raise ResourceExhaustedError(
                resource_type="memory",
                required=f"{required_memory:.1f}GB",
                available=f"{self._resource_usage.memory_available_gb:.1f}GB"
            )

        # Check total memory limit
        current_total = sum(
            status.memory_usage_gb for status in self._model_usage.values()
            if status.is_loaded
        )

        if current_total + required_memory > self.max_memory_gb:
            raise ResourceExhaustedError(
                resource_type="total_model_memory",
                required=f"{current_total + required_memory:.1f}GB",
                available=f"{self.max_memory_gb:.1f}GB"
            )

    def _manage_memory_pressure(self, required_memory_gb: float) -> None:
        """
        Manage memory pressure by unloading unused models.

        Args:
            required_memory_gb: Amount of memory needed
        """
        with self._lock:
            # Calculate current usage
            current_total = sum(
                status.memory_usage_gb for status in self._model_usage.values()
                if status.is_loaded
            )

            # Check if we need to free memory
            if current_total + required_memory_gb <= self.max_memory_gb:
                return

            # Find candidates for unloading (least recently used)
            candidates = [
                (name, status) for name, status in self._model_usage.items()
                if status.is_loaded and status.last_used is not None
            ]

            # Sort by last used time (oldest first)
            candidates.sort(key=lambda x: x[1].last_used)

            memory_to_free = (current_total + required_memory_gb) - self.max_memory_gb

            for model_name, status in candidates:
                if memory_to_free <= 0:
                    break

                self.logger.info(
                    f"Unloading {model_name} to free memory "
                    f"(last used: {status.last_used})"
                )

                self._unload_model(model_name)
                memory_to_free -= status.memory_usage_gb

    def _update_model_usage(self, model_name: str) -> None:
        """Update usage statistics for a model."""
        with self._lock:
            if model_name in self._model_usage:
                self._model_usage[model_name].last_used = datetime.now()
                self._model_usage[model_name].usage_count += 1

    def _start_resource_monitoring(self) -> None:
        """Start background resource monitoring."""
        def monitor():
            while not self._stop_monitoring.wait(10):  # Check every 10 seconds
                try:
                    self._update_resource_usage()
                    self._cleanup_unused_models()
                except Exception as e:
                    self.logger.error(f"Resource monitoring error: {e}")

        self._resource_monitor_thread = threading.Thread(
            target=monitor,
            name="ModelRegistry-ResourceMonitor",
            daemon=True
        )
        self._resource_monitor_thread.start()

    def _update_resource_usage(self) -> None:
        """Update current resource usage metrics."""
        memory = psutil.virtual_memory()

        self._resource_usage = ResourceUsage(
            memory_used_gb=memory.used / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            memory_percent=memory.percent,
            cpu_percent=psutil.cpu_percent(),
        )

        # Try to get GPU memory if available
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.mem_get_info()
                self._resource_usage.gpu_memory_available_gb = gpu_memory[0] / (1024**3)
                self._resource_usage.gpu_memory_used_gb = (
                    (gpu_memory[1] - gpu_memory[0]) / (1024**3)
                )
        except ImportError:
            pass  # PyTorch not available

    def _cleanup_unused_models(self) -> None:
        """Cleanup models that haven't been used recently."""
        with self._lock:
            current_time = datetime.now()
            timeout = timedelta(minutes=30)  # Default timeout

            for model_name, status in self._model_usage.items():
                if (status.is_loaded and
                    status.last_used and
                    current_time - status.last_used > timeout):

                    self.logger.info(f"Auto-unloading unused model: {model_name}")
                    self._unload_model(model_name)

    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models."""
        with self._lock:
            return list(self._models.keys())

    def get_model_status(self, model_name: str) -> Optional[ModelStatus]:
        """Get status information for a model."""
        return self._model_usage.get(model_name)

    def get_all_model_status(self) -> Dict[str, ModelStatus]:
        """Get status for all registered models."""
        with self._lock:
            return self._model_usage.copy()

    def get_resource_usage(self) -> Optional[ResourceUsage]:
        """Get current resource usage."""
        return self._resource_usage

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Dictionary with health status
        """
        try:
            with self._lock:
                healthy_models = 0
                total_models = len(self._models)

                model_health = {}
                for name, model in self._models.items():
                    health = model.health_check()
                    model_health[name] = health
                    if health['healthy']:
                        healthy_models += 1

                return {
                    'registry_healthy': True,
                    'loaded_models': total_models,
                    'healthy_models': healthy_models,
                    'resource_usage': self._resource_usage.__dict__ if self._resource_usage else None,
                    'model_health': model_health,
                    'memory_usage_gb': sum(
                        status.memory_usage_gb for status in self._model_usage.values()
                        if status.is_loaded
                    ),
                    'last_check': datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'registry_healthy': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

    def shutdown(self) -> None:
        """Shutdown the registry and cleanup resources."""
        self.logger.info("Shutting down ModelRegistry")

        # Stop monitoring
        self._stop_monitoring.set()
        if self._resource_monitor_thread:
            self._resource_monitor_thread.join(timeout=5)

        # Unload all models
        with self._lock:
            for model_name in list(self._models.keys()):
                self._unload_model(model_name)

        self.logger.info("ModelRegistry shutdown complete")

    def __del__(self):
        """Cleanup on object destruction."""
        try:
            self.shutdown()
        except Exception:
            pass  # Avoid exceptions during garbage collection


# Global registry instance
_global_registry: Optional[ModelRegistry] = None
_registry_lock = threading.Lock()


def get_global_registry() -> ModelRegistry:
    """
    Get the global model registry instance.

    Returns:
        Global ModelRegistry instance
    """
    global _global_registry

    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                deployment_profile = "development"  # Default, can be configured
                _global_registry = ModelRegistry(deployment_profile)

    return _global_registry


def shutdown_global_registry() -> None:
    """Shutdown the global registry."""
    global _global_registry

    if _global_registry is not None:
        _global_registry.shutdown()
        _global_registry = None